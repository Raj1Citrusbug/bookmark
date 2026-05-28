# Standard library imports
import sys
import traceback

# Third-party imports
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError

# Local application imports
from app.config.settings import app_settings
from app.utils.custom_exception import CustomException
from app.utils.messages.custom_response_messages import get_response_message
from app.utils.helpers.common_functions import extract_message_from_integrity_error
from app.config.logger import logger


class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling exceptions across all routes.

    This middleware catches various exceptions, logs the errors,
    and returns appropriate JSON responses with status codes.
    """

    async def dispatch(self, request: Request, call_next):
        """
        Handles exceptions and returns a JSON response with a status code.

        If an exception is caught, it logs the error and returns a JSON response
        with a status code. It also adds the "Access-Control-Allow-Origin" header
        to the response.

        Args:
            request (Request): The incoming request.
            call_next (Callable): The next middleware or route.

        Returns:
            Response: The JSON response with a status code.
        """
        try:
            response = await call_next(request)

        except HTTPException as http_exc:
            response = JSONResponse(
                status_code=http_exc.status_code,
                content={
                    "success": False,
                    "message": (
                        str(http_exc)
                        if app_settings.DEBUG
                        else get_response_message("common_message")
                    ),
                },
            )
        except ResponseValidationError as exc:
            logger.error(
                f"A response validation error occurred: {exc} at {exc.__traceback__.tb_lineno}"
            )
            error_details = exc.errors()
            formatted_message = "; ".join(
                f"{err['loc'][-1]}: {err['msg']}" for err in error_details
            )
            # Return a custom response
            if app_settings.DEBUG:
                response = JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    content={
                        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
                        "message": formatted_message,
                        "data": None,
                    },
                )
            else:
                response = JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={
                        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "message": get_response_message("common_message"),
                        "data": None,
                    },
                )

        except CustomException as custom_exc:
            response = JSONResponse(
                status_code=custom_exc.status_code,
                content={
                    "success": False,
                    "message": custom_exc.message,
                    "status_code": custom_exc.status_code,
                },
            )

        except IntegrityError as ie:
            logger.error(f"Error raised for IntegrityError: {ie.orig}")

            # TODO: This is for debugging purposes only and should be removed in production
            print("\n" + "=" * 80)
            print("⚠️  DATABASE INTEGRITY ERROR  ⚠️")
            print("=" * 80)
            print(f"Error Message: {str(ie.orig) if ie.orig else str(ie)}")
            print("=" * 80 + "\n")

            response = JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "success": False,
                    "message": extract_message_from_integrity_error(
                        str(ie.orig) if ie.orig else str(ie)
                    ),
                    "status_code": status.HTTP_409_CONFLICT,
                    "error": {
                        "error": (
                            str(ie)
                            if app_settings.DEBUG
                            else get_response_message("common_message")
                        ),
                    },
                },
            )

        except Exception as exception:
            logger.error(f"Exception: {str(exception)}")

            # TODO: This is for debugging purposes only and should be removed in production
            _, _, exc_traceback = sys.exc_info()
            traceback_details = traceback.extract_tb(exc_traceback)

            # Print to terminal
            print("\n" + "=" * 80)
            print("❌  INTERNAL SERVER ERROR  ❌")
            print("=" * 80)
            print(f"Error Type: {type(exception).__name__}")
            print(f"Error Message: {str(exception)}")

            if traceback_details:
                # Get the last frame that is relevant (usually the last one in the list)
                filename, line, func, text = traceback_details[-1]
                print("-" * 40)
                print(f"📍 File: {filename}")
                print(f"🔢 Line: {line}")
                print(f"📌 Function: {func}")
                print(f"📝 Code: {text}")
                print("-" * 40)

            # Also print the full traceback for context if needed, or keep it clean as requested.
            # traceback.print_exc() # Uncomment if full stack trace is desired in terminal

            print("=" * 80 + "\n")

            logger.debug(
                "******************************************************************** EXCEPTION STARTED ********************************************************************"
            )
            logger.debug(
                f"File path: {exception.__traceback__.tb_frame.f_code.co_filename}:{exception.__traceback__.tb_lineno}"
            )
            logger.debug(
                "******************************************************************** EXCEPTION ENDED ********************************************************************"
            )
            response = JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": (
                        str(exception)
                        if app_settings.DEBUG
                        else get_response_message("common_message")
                    ),
                    "error_type": "Exception",
                },
            )
        origin = (
            request.headers.get("origin").rstrip("/")
            if request.headers.get("origin")
            else ""
        )

        if origin in app_settings.get_allowed_origin_settings.get("allow_origins"):
            response.headers["Access-Control-Allow-Origin"] = origin
        else:
            response.headers["Access-Control-Allow-Origin"] = ""

        return response
