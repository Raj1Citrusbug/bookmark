# Third-party imports
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

# Local application imports
from app.api.auth.routers.auth import auth_router, user_router
from app.api.bookmark.routers.bookmark import router as bookmark_router
from app.api.tag.routers.tag import router as tag_router
from app.api.admin.routers.admin import router as admin_router

from app.config.settings import app_settings

from app.utils.middleware.exception_handler.custom_exception import (
    GlobalExceptionMiddleware,
)
from app.utils.middleware.exception_handler.request_validator import RequestValidator
from app.utils.scheduler import (
    start_scheduler,
    shutdown_scheduler,
    add_weekly_broken_link_check_task,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle hook for the FastAPI application.
    Creates tables, seeds admin user, and runs the background scheduler.
    """
    # Start background scheduler
    add_weekly_broken_link_check_task()
    start_scheduler()

    try:
        yield
    finally:
        # Shutdown scheduler
        shutdown_scheduler()


app = FastAPI(
    debug=app_settings.DEBUG,
    title=app_settings.APP_NAME,
    version=app_settings.APP_VERSION,
    redirect_slashes=False,
    root_path=app_settings.APP_PREFIX,
    docs_url="/docs" if app_settings.DEBUG else None,
    redoc_url="/redoc" if app_settings.DEBUG else None,
    lifespan=lifespan,
)

# Global Exception Middleware
app.add_middleware(GlobalExceptionMiddleware)


# Pydantic validation error handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """
    Handles request validation exceptions by formatting using RequestValidator.
    """
    user_message = RequestValidator().format_pydantic_errors(exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"success": False, "message": user_message},
    )


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    **app_settings.get_allowed_origin_settings,
)

# Register routers
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(bookmark_router)
app.include_router(tag_router)
app.include_router(admin_router)


@app.get("/health", include_in_schema=False)
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ok"},
    )
