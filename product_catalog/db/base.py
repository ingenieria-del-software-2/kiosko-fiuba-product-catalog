from sqlalchemy.orm import DeclarativeBase

from product_catalog.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
