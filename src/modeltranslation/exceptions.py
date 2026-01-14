class ImproperlyConfiguredError(Exception):
    """Raised when the configuration is internally inconsistent."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
