class CustomException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int,
    ):
        """
        Initializes a new instance of CustomException, which represents
        an exception that is thrown when a custom exception occurs.

        Args:
        - message (str): The message to return with the exception.
        - status_code (int): The HTTP status code to return with the exception.
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)
