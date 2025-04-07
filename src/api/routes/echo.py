"""API routes for echo messages."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class Message(BaseModel):
    """Message schema for echo endpoint."""

    message: str


@router.post("/", response_model=Message, name="send_echo_message")
async def send_echo_message(
    incoming_message: Message,
) -> Message:
    """
    Sends echo back to user.

    Args:
        incoming_message: incoming message.

    Returns:
        Message same as the incoming.
    """
    return incoming_message
