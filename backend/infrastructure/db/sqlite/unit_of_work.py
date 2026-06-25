"""
ARCH-7: Unit of Work (Transaction Boundaries)
Ensures all operations within a Use Case execute inside a single
atomic transaction: if anything fails → automatic rollback.
"""

from contextlib import contextmanager
from typing import Generator

from backend.infrastructure.db.sqlite.database import Database
from backend.infrastructure.db.sqlite.repositories import (
    EventRepository,
    SessionRepository,
    IntentRepository,
)


class UnitOfWork:
    """
    Groups repos under a single SQLite transaction.

    Usage in a Use Case:
        with UnitOfWork(db) as uow:
            uow.events.insert(event)
            uow.sessions.create(session)
            uow.commit()        # explicit commit at the end
        # If any exception is raised → automatic rollback
    """

    def __init__(self, db: Database):
        self._db = db
        self.events = EventRepository(db)
        self.sessions = SessionRepository(db)
        self.intents = IntentRepository(db)

    def __enter__(self) -> "UnitOfWork":
        # Disable individual auto-commits during the transaction
        self._db.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Any exception → full rollback
            try:
                self._db._get_connection().rollback()
            except Exception:
                pass
            return False  # re-raise the original exception
        return False

    def commit(self):
        """Commits all changes in the current transaction."""
        self._db.commit()

    def rollback(self):
        """Rolls back all changes in the current transaction."""
        self._db._get_connection().rollback()


@contextmanager
def transaction(db: Database) -> Generator[UnitOfWork, None, None]:
    """
    Functional alternative to the class-based context manager.

    Usage:
        with transaction(db) as uow:
            uow.events.insert(...)
            uow.sessions.create(...)
            uow.commit()
    """
    uow = UnitOfWork(db)
    try:
        uow._db.execute("BEGIN")
        yield uow
    except Exception:
        uow.rollback()
        raise
