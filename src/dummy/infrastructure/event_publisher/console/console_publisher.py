"""Console implementation of the event publisher."""

import json
import logging
from dataclasses import asdict
from datetime import datetime
from typing import Any

from src.dummy.infrastructure.event_publisher.interfaces.event_publisher import (
    EventPublisher,
)

logger = logging.getLogger(__name__)


class ConsoleEventPublisher(EventPublisher):
    """Console implementation of the event publisher that prints events to console."""

    async def publish(self, event: Any) -> None:
        """
        Publish a domain event by logging it to the console.

        Args:
            event: The domain event to publish
        """
        event_type = event.__class__.__name__
        event_data = asdict(event)

        # Convert datetime objects to ISO format strings for JSON serialization
        for key, value in event_data.items():
            if isinstance(value, datetime):
                event_data[key] = value.isoformat()

        # Use WARNING level instead of INFO to make events more visible in logs
        logger.warning(
            "*** DOMAIN EVENT *** [%s]: %s",
            event_type,
            json.dumps(event_data),
        )
