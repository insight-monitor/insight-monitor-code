from abc import ABC, abstractmethod
from typing import Any, List, Optional


class IEventRepository(ABC):
    @abstractmethod
    def insert(self, event: dict[str, Any]) -> int:
        pass

    @abstractmethod
    def insert_batch(self, events: List[dict[str, Any]]) -> None:
        pass

    @abstractmethod
    def find_by_session(self, session_id: str) -> List[dict]:
        pass

    @abstractmethod
    def find_recent(self, limit: int = 50) -> List[dict]:
        pass

    @abstractmethod
    def find_unassigned(self) -> List[dict]:
        pass

    @abstractmethod
    def assign_to_session(self, event_id: str, session_id: str) -> None:
        pass


class ISessionRepository(ABC):
    @abstractmethod
    def create(self, session: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def update(self, session_id: str, updates: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def find_all(self, status: Optional[str] = None, limit: int = 50) -> List[dict]:
        pass

    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[dict]:
        pass


class IIntentRepository(ABC):
    @abstractmethod
    def create(self, record: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def find_by_session(self, session_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def find_all(self, limit: int = 50) -> List[dict]:
        pass
