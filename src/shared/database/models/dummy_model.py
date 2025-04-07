"""SQLAlchemy model for Dummy entity."""

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import String

from product_catalog.infrastructure.database.base import Base


class DummyModel(Base):
    """Database model for Dummy entity."""

    __tablename__ = "dummy_model"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(length=200))
