from backend.domain.ports.repositories import IEventRepository
from backend.domain.entities.raw_event import RawEvent


class IngestEventUseCase:
    def __init__(self, event_repo: IEventRepository):
        self.event_repo = event_repo

    def execute(self, event: RawEvent) -> str:
        event_dict = event.model_dump()
        event_dict["timestamp"] = event.timestamp.isoformat()
        self.event_repo.insert(event_dict)
        return event.event_id

    def execute_batch(self, events: list[RawEvent]) -> int:
        for event in events:
            self.execute(event)
        return len(events)
