from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional
from PySide6.QtCore import QObject, Signal


@dataclass(frozen=True)
class Event:
    type: str
    payload: Any = None
    source: Optional[str] = None


class EventBus(QObject):
    event_emitted = Signal(object)

    def publish(self, event: Event) -> None:
        self.event_emitted.emit(event)

    def publish_type(self, event_type: str, payload: Any = None, source: Optional[str] = None) -> None:
        self.publish(Event(type=event_type, payload=payload, source=source))

    def subscribe(
        self,
        callback: Callable[[Event], None],
        *,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Callable[[], None]:
        def _handler(event: Event) -> None:
            if event_type is not None and event.type != event_type:
                return

            if source is not None and event.source != source:
                return

            callback(event)

        self.event_emitted.connect(_handler)

        def _unsubscribe() -> None:
            try:
                self.event_emitted.disconnect(_handler)

            except (TypeError, RuntimeError):
                pass

        return _unsubscribe
