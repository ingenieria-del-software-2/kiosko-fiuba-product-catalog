"""DTOs for the dummy domain."""

from pydantic import BaseModel, Field


class DummyDTO(BaseModel):
    """DTO for Dummy entity."""

    id: int
    name: str


class CreateDummyDTO(BaseModel):
    """DTO for creating a new Dummy entity."""

    name: str = Field(..., min_length=1)
