# Standard library imports
from typing import Any, Dict, List


class RequestValidator:
    """
    Formats Pydantic errors into a human-readable string.

    Attributes:
        None

    Methods:
        format_pydantic_errors(errors: List[Dict[str, Any]]) -> str:
            Formats Pydantic errors into a human-readable string.
    """

    def format_pydantic_errors(self, errors: List[Dict[str, Any]]) -> str:
        """
        Formats Pydantic errors into a human-readable string.

        Args:
            errors (List[Dict[str, Any]]): A list of dictionaries containing the error details.

        Returns:
            str: A human-readable string containing the formatted error messages.
        """
        messages = []

        for error in errors:
            # Extract field name safely
            loc = error.get("loc", [])
            field_name = loc[-1] if loc else "field"

            # Convert snake_case -> Human readable
            field_name = str(field_name).replace("_", " ").capitalize()

            error_type = error.get("type")
            error_msg = error.get("msg", "Invalid value")
            ctx = error.get("ctx") or {}

            received_val = None
            match error_type:
                case "missing":
                    messages.append(f"{field_name} is required.")
                case "string_too_short":
                    min_len = ctx.get("min_length")
                    if isinstance(received_val, str) and isinstance(min_len, int):
                        messages.append(
                            f"{field_name} is too short. Minimum is {min_len} characters, "
                            f"but received {len(received_val)}."
                        )
                    elif isinstance(min_len, int):
                        messages.append(
                            f"{field_name} is too short. Minimum is {min_len} characters."
                        )
                    else:
                        messages.append(f"{field_name} is too short.")

                case "string_too_long":
                    max_len = ctx.get("max_length")
                    if isinstance(received_val, str) and isinstance(max_len, int):
                        extra = len(received_val) - max_len
                        messages.append(
                            f"{field_name} is too long. Maximum is {max_len} characters, "
                            f"but received {len(received_val)} (exceeded by {extra})."
                        )
                    elif isinstance(max_len, int):
                        messages.append(
                            f"{field_name} is too long. Maximum is {max_len} characters."
                        )
                    else:
                        messages.append(f"{field_name} is too long.")

                case "value_error.email":
                    messages.append(f"Please enter a valid {field_name}.")
                case _:
                    messages.append(f"{field_name}: {error_msg}")

        # Join multiple errors into a single message
        return " ".join(messages)
