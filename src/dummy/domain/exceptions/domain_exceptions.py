"""Domain exceptions module."""


class DomainError(Exception):
    """Base exception for all domain errors."""


class DummyNotFoundError(DomainError):
    """Raised when a dummy entity is not found."""


class InvalidDummyError(DomainError):
    """Raised when a dummy entity is invalid."""
