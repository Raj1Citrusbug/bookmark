# Standard library imports
from typing import TypedDict

# Third-party imports
from pydantic_settings import BaseSettings, SettingsConfigDict


class AllowedOriginResponseDict(TypedDict):
    """
    This is a TypedDict for allowed origin response.
    """
    allow_origins: list
    allow_headers: list
    allow_methods: list


class AppSettings(BaseSettings):
    # APP Configurations
    APP_NAME: str = "Bookmark Manager"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    APP_PREFIX: str = ""

    # CORS Configurations
    ALLOWED_ORIGINS: str
    ALLOWED_METHODS: str
    ALLOWED_HEADERS: str

    # Database Configurations
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    REDIS_URL: str
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800
    DB_ECHO: bool = False
    DB_AUTOFLUSH: bool = False
    DB_AUTOCOMMIT: bool = False

    # Logger Configurations
    LOGGER_NAME: str = "bookmark_logger"
    INTERVAL: int = 1
    LOG_BACKUP_COUNT: int = 7

    # Auth Configurations
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    BCRYPT_SALT_ROUNDS: int = 12

    # Lifetime Configurations (format: days,hours,minutes,seconds)
    JWT_ACCESS_TOKEN_LIFETIME: str = "0,1,0,0"
    JWT_REMEMBER_ME_LIFETIME: str = "7,0,0,0"
    JWT_REFRESH_TOKEN_LIFETIME: str = "30,0,0,0"
    JWT_VERIFICATION_TOKEN_LIFETIME: str = "1,0,0,0"
    JWT_FORGOT_PASSWORD_TOKEN_LIFETIME: str = "0,0,15,0"

    # Email Config
    FROM_EMAIL: str

    # Dynamically set the environment file
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def get_allowed_origin_settings(self) -> AllowedOriginResponseDict:
        """
        Function to return allowed origins, headers, and methods.
        """
        return {
            "allow_origins": self.ALLOWED_ORIGINS.split(","),
            "allow_headers": self.ALLOWED_HEADERS.split(","),
            "allow_methods": self.ALLOWED_METHODS.split(","),
        }


# Load settings
app_settings = AppSettings()
