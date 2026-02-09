from datetime import datetime
from uuid import uuid4
from source.utils.LogManager import LogManager


class Tarefa:
    def __init__(self, titulo, descricao="", etapas=None, prioridade="Média", status="Todo", id=None):
        self.titulo = titulo
        self.descricao = descricao
        self.etapas = etapas or []
        self.prioridade = self.normalizar_prioridade(prioridade)
        self.status = status
        self.data_criacao = datetime.now().isoformat()
        self.pomodoros_completados = 0
        self.id = id or str(uuid4())
        self.logger = LogManager.get_logger()

    def to_dict(self):
        try:
            return {
                'id': self.id,
                'titulo': self.titulo,
                'descricao': self.descricao,
                'etapas': self.etapas,
                'prioridade': self.prioridade,
                'status': self.status,
                'data_criacao': self.data_criacao,
                'pomodoros': self.pomodoros_completados
            }

        except Exception as e:
            self.logger.error(f"Erro ao converter tarefa para dicionário: {str(e)}", exc_info=True)
            return {}

    @staticmethod
    def from_dict(data):
        try:
            prioridade = Tarefa.normalizar_prioridade(data.get('prioridade', 'Média'))
            tarefa = Tarefa(
                data['titulo'],
                data.get('descricao', ''),
                data.get('etapas', []),
                prioridade,
                data.get('status', 'Todo'),
                id=data.get('id', str(uuid4()))
            )
            tarefa.data_criacao = data.get('data_criacao', datetime.now().isoformat())
            tarefa.pomodoros_completados = data.get('pomodoros', 0)
            return tarefa

        except Exception as e:
            logger = LogManager.get_logger()
            logger.error(f"Erro ao criar tarefa a partir de dicionário: {str(e)}", exc_info=True)
            return None

    @staticmethod
    def normalizar_prioridade(valor):
        try:
            if not valor:
                return "Média"

            v = str(valor).strip().lower()
            mapa = {
                "alta": "Alta",
                "high": "Alta",
                "🔴": "Alta",
                "média": "Média",
                "media": "Média",
                "medium": "Média",
                "🟡": "Média",
                "baixa": "Baixa",
                "low": "Baixa",
                "🟢": "Baixa",
            }

            if v.startswith("🔴"):
                return "Alta"

            if v.startswith("🟡"):
                return "Média"

            if v.startswith("🟢"):
                return "Baixa"

            return mapa.get(v, "Média")

        except Exception:
            return "Média"
