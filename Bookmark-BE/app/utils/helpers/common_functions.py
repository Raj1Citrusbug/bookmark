import re

INTEGRITY_REGEX = r"Key \((\w+)\)=\((.+?)\)"
URL_REGEX = r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$"
PASSWORD_REGEX = r"^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-])[^\s]{8,}$"

def extract_message_from_integrity_error(error_message: str) -> str:
    """
    Extracts the message from IntegrityError and formats the message.

    Args:
        error_message (str): The raw error message from IntegrityError.

    Returns:
        str: Formatted error message
    """
    match = re.search(INTEGRITY_REGEX, error_message)
    if match:
        field, _ = match.groups()
        field = str(field).replace("_", " ").capitalize()
        return f"The {field} already exists."
    return "A database integrity error occurred."
