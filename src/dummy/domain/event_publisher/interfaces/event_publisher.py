"""Event publisher interface."""

from abc import ABC, abstractmethod
from typing import Any


class EventPublisher(ABC):
    """Interface for event publishers."""

    @abstractmethod
    async def publish(self, event: Any) -> None:
        """
        Publish a domain event.

        Args:
            event: The domain event to publish
        """
