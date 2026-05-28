# Standard library imports
from typing import Literal

keys = Literal[
    "login_success",
    "user_not_found",
    "user_not_active",
    "token_generation_failed",
    "invalid_credentials",
    "common_message",
    "user_already_exists",
    "signup_success",
    "not_found",
    "permission_denied",
    "invalid_token",
    "token_expired",
    "create_success",
    "update_success",
    "detail_success",
    "delete_success",
    "tag_already_exists",
]

response_dict = {
    "login_success": "User logged in successfully",
    "user_not_found": "User not found with the provided {}",
    "user_not_active": "Your account is not active. Please contact the admin.",
    "token_generation_failed": "Failed to generate {} token",
    "invalid_credentials": "Invalid credentials provided",
    "common_message": "Unable to process the request. Please try again later",
    "user_already_exists": "A user with this {} already exists",
    "signup_success": "User registered successfully.",
    "not_found": "{} not found",
    "permission_denied": "You do not have permission to perform this action",
    "invalid_token": "Invalid token",
    "token_expired": "Token has expired",
    "create_success": "{} created successfully.",
    "update_success": "{} updated successfully.",
    "detail_success": "{} fetched successfully.",
    "delete_success": "{} deleted successfully.",
    "tag_already_exists": "A tag with this {} already exists",
}


def get_response_message(key: keys, *args) -> str:
    """
    Retrieve a custom response message based on the provided key.

    Args:
        key (Literal): A key from the response_dict.
        *args: Optional arguments to be formatted into the response message.

    Returns:
        str: The custom response message.
    """
    try:
        return response_dict[key].format(*args)
    except KeyError:
        return key
