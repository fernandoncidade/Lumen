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
        self._pending_conceitos = []

    def send_conceito(self, dados: dict) -> None:
        try:
            self._pending_conceitos.append(dados)
            self.conceito_atualizado.emit(dados)

        except Exception:
            pass

    def drain_pending_conceitos(self) -> None:
        try:
            if not self._pending_conceitos:
                return

            for dados in list(self._pending_conceitos):
                try:
                    self.conceito_atualizado.emit(dados)

                except Exception:
                    pass

            self._pending_conceitos.clear()

        except Exception:
            pass

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance


def get_event_bus() -> EventBus:
    return EventBus.get_instance()
