"""Domain events module."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class DomainEvent:
    """Base class for all domain events."""

    # Use field with default_factory to ensure this is properly handled as a default
    occurred_on: datetime = field(default_factory=datetime.now)


@dataclass
class DummyCreatedEvent:
    """Event fired when a dummy entity is created."""

    dummy_id: int
    name: str
    occurred_on: datetime = field(default_factory=datetime.now)
