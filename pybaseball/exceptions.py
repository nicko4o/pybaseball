class PybaseballError(Exception):
    """Base exception for all pybaseball errors."""
    pass


class PybaseballNetworkError(PybaseballError):
    """Base exception for all network related errors."""
    pass


class PybaseballTimeoutError(PybaseballNetworkError):
    """Exception raised when a network request times out."""
    pass


class PybaseballHttpError(PybaseballNetworkError):
    """Exception raised when an HTTP request returns an error status code."""
    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code
