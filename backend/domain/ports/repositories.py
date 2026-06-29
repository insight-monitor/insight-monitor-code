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
    def find_by_session_paginated(self, session_id: str, limit: int = 20, offset: int = 0) -> List[dict]:
        pass

    @abstractmethod
    def count_by_session(self, session_id: str) -> int:
        pass

    @abstractmethod
    def find_recent(self, limit: int = 50, offset: int = 0) -> List[dict]:
        pass

    @abstractmethod
    def count_all(self) -> int:
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
    def count_all(self, status: Optional[str] = None) -> int:
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


class ITicketRepository(ABC):
    @abstractmethod
    def create(self, ticket: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def find_all(self, status: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[dict]:
        pass

    @abstractmethod
    def count_all(self, status: Optional[str] = None) -> int:
        pass

    @abstractmethod
    def find_by_id(self, ticket_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def update(self, ticket_id: str, updates: dict[str, Any]) -> None:
        pass

    @abstractmethod
    def delete(self, ticket_id: str) -> None:
        pass

    @abstractmethod
    def stat_counts(self) -> dict[str, int]:
        pass


class ICommentRepository(ABC):
    @abstractmethod
    def create(self, comment: dict[str, Any]) -> str:
        pass

    @abstractmethod
    def find_by_ticket(self, ticket_id: str) -> List[dict]:
        pass

    @abstractmethod
    def find_by_id(self, comment_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    def delete_by_ticket(self, ticket_id: str) -> None:
        pass
