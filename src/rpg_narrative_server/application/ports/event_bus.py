from typing import Protocol, Callable


class EventBus(Protocol):
    def publish(self, event: object) -> None: ...

    def subscribe(self, event_type: type, handler: Callable) -> None: ...
