"""Library-specific exception hierarchy."""


class PureDataError(Exception):
    """Base exception for PureData."""


class SchemaValidationError(PureDataError):
    """Raised when a schema constraint is violated."""

    def __init__(self, message: str, column: str | None = None) -> None:
        self.column = column
        super().__init__(message)


class MissingColumnError(SchemaValidationError):
    """Requested column does not exist."""

    def __init__(self, column: str, available: list[str]) -> None:
        super().__init__(
            f"Column '{column}' not found. Available: {', '.join(available)}",
            column=column,
        )


class EmptyDatasetError(PureDataError):
    """Input dataset is completely empty."""


class StrategyNotFoundError(PureDataError):
    """No appropriate strategy found for the given format/column."""
