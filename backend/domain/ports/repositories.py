from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any, Optional


class IEventRepository(ABC):
    @abstractmethod
    def insert(self, event: dict[str, Any]) -> int: ...

    @abstractmethod
    def insert_batch(self, events: Sequence[dict[str, Any]]) -> None: ...

    @abstractmethod
    def find_by_session(self, session_id: str) -> list[dict]: ...

    @abstractmethod
    def find_recent(self, limit: int = 50) -> list[dict]: ...

    @abstractmethod
    def find_unassigned(self) -> list[dict]: ...

    @abstractmethod
    def assign_to_session(self, event_id: str, session_id: str) -> None: ...


class ISessionRepository(ABC):
    @abstractmethod
    def create(self, session: dict[str, Any]) -> str: ...

    @abstractmethod
    def update(self, session_id: str, updates: dict[str, Any]) -> None: ...

    @abstractmethod
    def find_all(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict]: ...

    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[dict]: ...

    @abstractmethod
    def count_all(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> int: ...


class IIntentRepository(ABC):
    @abstractmethod
    def create(self, record: dict[str, Any]) -> str: ...

    @abstractmethod
    def find_by_session(self, session_id: str) -> Optional[dict]: ...

    @abstractmethod
    def find_all(self, limit: int = 50) -> list[dict]: ...
