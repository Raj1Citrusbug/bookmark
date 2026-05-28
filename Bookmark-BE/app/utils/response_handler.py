from typing import Any, Optional
from app.utils.custom_exception import CustomException
from app.config.logger import logger


class ResponseHandler:
    """
    Custom response handler for consistent API responses.
    """

    @staticmethod
    def success(
        message: str = "Success",
        data: Optional[Any] = None,
    ) -> dict:
        """
        Standardized success response.
        """
        return dict(success=True, data=data, message=message)

    @staticmethod
    def success_listing(
        message: str = "Success",
        data: Optional[Any] = None,
        count: Optional[int] = None,
    ) -> dict:
        """
        Standardized success response for listings with count.
        """
        return dict(success=True, data=data, message=message, count=count)

    @staticmethod
    def error(
        exception: Exception,
        message: str = "Something went wrong",
    ) -> dict:
        """
        Standardized error response.
        """
        if isinstance(exception, CustomException):
            return dict(success=False, message=exception.message, data=None)

        logger.error(f"Exception: {str(exception)}")
        return dict(success=False, message=message, data=None)
