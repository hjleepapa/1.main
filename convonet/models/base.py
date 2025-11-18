"""
Shared SQLAlchemy Declarative Base for Convonet models.

Some parts of the codebase (team dashboard, todo service, WebRTC transfer stack)
expect to import ``Base`` from ``convonet.models.base``.  The file was moved to
the archive during cleanup, which caused runtime imports to fail on Render and
prevented our blueprints from registering.  This module restores the shared base
definition so every model (user/team + DB todo tables) can inherit from the same
metadata object.
"""

from __future__ import annotations

from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """Central declarative base class for all Convonet SQLAlchemy models."""

    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:  # type: ignore[misc]
        """
        Provide a sensible default table name.

        Individual models can still override ``__tablename__`` explicitly (as
        the authentication/teams models already do).  For any models that omit
        it (e.g., some of the todo/calendar tables), this keeps the naming
        consistent and prevents SQLAlchemy from falling back to less predictable
        defaults.
        """

        return cls.__name__.lower()


__all__ = ["Base"]

