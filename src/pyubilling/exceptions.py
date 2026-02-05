class UbillingError(Exception):
    """Base exception for all pyubilling errors."""


class UbillingConnectionError(UbillingError):
    """Raised when the API endpoint is unreachable or times out."""


class UbillingAuthError(UbillingError):
    """Raised when credentials are missing or invalid."""


class UbillingResponseError(UbillingError):
    """Raised when the API returns a non-2xx HTTP status."""

    def __init__(self, message: str, *, status_code: int) -> None:
        super().__init__(message)
        self.status_code = status_code


class UbillingParseError(UbillingError):
    """Raised when the API response cannot be parsed as JSON or XML."""
