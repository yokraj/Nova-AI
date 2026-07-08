"""Database Base model class configuration for Nova AI.

Exposes the SQLAlchemy DeclarativeBase from which all application database models
inherit, tracking model schemas and fields.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models.

    Used by migrations and session setups to trace schema mappings.
    """

    pass
