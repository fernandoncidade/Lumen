from datetime import datetime
from uuid import uuid4
from source.utils.LogManager import LogManager


class Tarefa:
    def __init__(self, titulo, descricao="", etapas=None, prioridade="Importante e Urgente", status="Todo", id=None):
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
            prioridade = Tarefa.normalizar_prioridade(data.get('prioridade', 'Importante e Urgente'))
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
                return "Importante e Urgente"

            v_raw = str(valor).strip()
            v = v_raw.lower()

            p_iu = "Importante e Urgente"
            p_inu = "Importante, mas Não Urgente"
            p_niu = "Não Importante, mas Urgente"
            p_ninnu = "Não Importante e Não Urgente"

            if v.startswith("🔴"):
                return p_iu

            if v.startswith("🟠"):
                return p_inu

            if v.startswith("🟢"):
                return p_ninnu

            if v.startswith("🟡"):
                if "média" in v or "media" in v or "medium" in v:
                    return p_inu

                return p_niu

            v_norm = (
                v.replace("não", "nao")
                .replace("ã", "a")
                .replace("á", "a")
                .replace("â", "a")
                .replace("é", "e")
                .replace("ê", "e")
                .replace("í", "i")
                .replace("ó", "o")
                .replace("ô", "o")
                .replace("ú", "u")
            )
            v_norm = " ".join(v_norm.replace(",", " ").split())

            if "importante" in v_norm and "urgente" in v_norm and "nao urgente" not in v_norm:
                if "nao importante" in v_norm:
                    return p_niu
                return p_iu

            if "importante" in v_norm and "nao urgente" in v_norm:
                if "nao importante" in v_norm:
                    return p_ninnu
                return p_inu

            if "nao importante" in v_norm and "urgente" in v_norm:
                return p_niu

            if "nao importante" in v_norm and "nao urgente" in v_norm:
                return p_ninnu

            mapa_legado = {
                "alta": p_iu,
                "high": p_iu,
                "media": p_inu,
                "média": p_inu,
                "medium": p_inu,
                "baixa": p_ninnu,
                "low": p_ninnu,
            }
            if v in mapa_legado:
                return mapa_legado[v]

            return p_iu

        except Exception:
            return "Importante e Urgente"
