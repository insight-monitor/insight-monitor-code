"""
ARCH-7: Unit of Work (Transaction Boundaries)
Garantiza que todas las operaciones de un Use Case se ejecuten dentro
de una sola transacción atómica: si algo falla → rollback automático.
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
    Agrupa repos bajo una sola transacción de SQLite.

    Uso en un Use Case:
        with UnitOfWork(db) as uow:
            uow.events.insert(event)
            uow.sessions.create(session)
            uow.commit()        # commit explícito al final
        # Si se lanza cualquier excepción → rollback automático
    """

    def __init__(self, db: Database):
        self._db = db
        self.events = EventRepository(db)
        self.sessions = SessionRepository(db)
        self.intents = IntentRepository(db)

    def __enter__(self) -> "UnitOfWork":
        # Desactivamos los auto-commits individuales durante la transacción
        self._db.execute("BEGIN")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            # Cualquier excepción → rollback total
            try:
                self._db._get_connection().rollback()
            except Exception:
                pass
            return False  # re-raise la excepción original
        return False

    def commit(self):
        """Confirma todos los cambios de la transacción actual."""
        self._db.commit()

    def rollback(self):
        """Deshace todos los cambios de la transacción actual."""
        self._db._get_connection().rollback()


@contextmanager
def transaction(db: Database) -> Generator[UnitOfWork, None, None]:
    """
    Alternativa funcional al context manager de clase.

    Uso:
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
