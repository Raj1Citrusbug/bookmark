from enum import Enum


class RoleType(Enum):
    """Enum representing Role Types."""

    ADMIN = "ADMIN"
    USER = "USER"


class TokenType(Enum):
    """Enum representing Token Types."""

    RESET_TOKEN = "reset"


class SortOrder(str, Enum):
    """Enum representing Sort Orders."""

    ASC = "asc"
    DESC = "desc"
