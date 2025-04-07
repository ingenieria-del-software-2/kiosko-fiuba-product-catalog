"""Console implementation of EventPublisher for logging domain events."""

import json
import logging
from typing import Any, Dict, List, Optional

from src.products.domain.event_publisher.event_publisher import EventPublisher
from src.products.domain.events.events import DomainEvent


class ConsoleEventPublisher(EventPublisher):
    """A simple event publisher that logs events to the console."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """Initialize the console event publisher.

        Args:
            logger: Optional logger instance. If not provided, a new one will
                be created.
        """
        self._logger = logger or logging.getLogger(__name__)

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event by logging it to the console.

        Args:
            event: The domain event to publish
        """
        event_dict = self._event_to_dict(event)
        self._logger.info(
            f"EVENT PUBLISHED: {event.event_type} - {json.dumps(event_dict, indent=2)}",
        )

    async def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple events by logging them to the console.

        Args:
            events: List of domain events to publish
        """
        for event in events:
            await self.publish(event)

    def _event_to_dict(self, event: DomainEvent) -> Dict[str, Any]:
        """Convert a domain event to a dictionary.

        Args:
            event: The domain event to convert

        Returns:
            A dictionary representation of the event
        """
        # Base event data
        event_dict = {
            "event_id": str(event.event_id),
            "event_type": event.event_type,
            "aggregate_id": str(event.aggregate_id),
            "occurred_on": event.occurred_on.isoformat(),
        }

        # Add all other attributes from the event
        for key, value in event.__dict__.items():
            if key not in event_dict and not key.startswith("_"):
                # Handle UUID and other special types
                if hasattr(value, "__str__") and not isinstance(
                    value,
                    (str, int, float, bool, list, dict),
                ):
                    event_dict[key] = str(value)
                else:
                    event_dict[key] = value

        return event_dict
