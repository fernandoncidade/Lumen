from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    conceito_atualizado = Signal(dict)
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        super().__init__()
        self._initialized = True

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance


def get_event_bus() -> EventBus:
    return EventBus.get_instance()
