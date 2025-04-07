"""Event publisher interface."""

from abc import ABC, abstractmethod

from src.products.domain.events.events import DomainEvent


class EventPublisher(ABC):
    """Interface for publishing domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""

    @abstractmethod
    async def publish_all(self, events: list[DomainEvent]) -> None:
        """Publish multiple domain events."""
