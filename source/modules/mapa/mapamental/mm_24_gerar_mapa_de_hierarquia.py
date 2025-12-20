from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QColor, QPen
from typing import Dict, List, Callable
from source.utils.LogManager import LogManager
from source.modules.mapa.mp_01_NoConceito import NoConceito
from source.modules.mapa.mp_02_LinhaConexao import LinhaConexao

logger = LogManager.get_logger()

def _montar_info_associadas(tr: Callable[[str, str], str], hierarquia: Dict, nivel: int, tipo_no: str) -> List[str]:
    info_associadas: List[str] = []

    resumo = hierarquia.get('resumo_contextual', '')
    if resumo:
        simbolo_nivel = {
            0: '📖',  # Documento
            1: '📗',  # Parte
            2: '📘',  # Capítulo
            3: '📙',  # Subcapítulo
            4: '📔'   # Sub-subcapítulo
        }.get(nivel, '📄')

        bloco_resumo = []
        bloco_resumo.append(
            tr("App", "{simbolo} RESUMO (Nível {nivel}):\n").format(
                simbolo=simbolo_nivel,
                nivel=nivel
            )
        )
        bloco_resumo.append(f"{resumo}\n")
        bloco_resumo.append("━" * 60)
        info_associadas.append("".join(bloco_resumo))

    conceitos = hierarquia.get('conceitos', [])
    if conceitos:
        bloco_conceitos = []
        bloco_conceitos.append(
            tr("App", "\n🎯 CONCEITOS-CHAVE ({quantidade}):\n").format(
                quantidade=len(conceitos)
            )
        )

        for idx, c in enumerate(conceitos[:10], 1):
            tipo_icon = {
                'entidade': '👤',
                'termo_tecnico': '🔧',
                'conceito': '💡'
            }.get(c.get('tipo'), '•')

            freq_info = ""
            if c.get('frequencia') is not None:
                freq_info = tr("App", "[freq: {frequencia}]").format(frequencia=c['frequencia'])

            bloco_conceitos.append(
                tr("App", "{idx}. {icon} {texto} (importância: {importancia:.2f}) {freq}\n").format(
                    idx=idx,
                    icon=tipo_icon,
                    texto=c.get('texto', ''),
                    importancia=float(c.get('importancia', 0.0)),
                    freq=freq_info
                )
            )

            if c.get('contextos') and len(c['contextos']) > 0:
                contexto = c['contextos'][0][:150]
                if len(c['contextos'][0]) > 150:
                    contexto += "..."

                bloco_conceitos.append(
                    tr("App", "   └─ Contexto: \"{contexto}\"\n").format(contexto=contexto)
                )

        bloco_conceitos.append("━" * 60)
        info_associadas.append("".join(bloco_conceitos))

    ideias = hierarquia.get('ideias_principais', [])
    if ideias:
        bloco_ideias = []
        bloco_ideias.append(
            tr("App", "\n💡 IDEIAS PRINCIPAIS ({quantidade}):\n\n").format(
                quantidade=len(ideias)
            )
        )

        for idx, ideia in enumerate(ideias[:8], 1):
            importancia = float(ideia.get('importancia', 0.0))
            importancia_barra = "█" * int(importancia * 10)
            bloco_ideias.append(
                tr("App", "{idx}. [{barra}] Importância: {importancia:.2f}\n").format(
                    idx=idx,
                    barra=importancia_barra,
                    importancia=importancia
                )
            )
            bloco_ideias.append(
                tr("App", "   \"{texto}\"\n\n").format(texto=ideia.get('texto', ''))
            )

        bloco_ideias.append("━" * 60)
        info_associadas.append("".join(bloco_ideias))

    texto_puro = hierarquia.get('texto_puro', '')
    if texto_puro:
        num_palavras = len(texto_puro.split())
        num_caracteres = len(texto_puro)
        num_paragrafos = len([p for p in texto_puro.split('\n\n') if p.strip()])

        bloco_estatisticas = []
        bloco_estatisticas.append(tr("App", "\n📊 ESTATÍSTICAS:\n"))
        bloco_estatisticas.append(tr("App", "   • Palavras: {valor}\n").format(valor=f"{num_palavras:,}"))
        bloco_estatisticas.append(tr("App", "   • Caracteres: {valor}\n").format(valor=f"{num_caracteres:,}"))
        bloco_estatisticas.append(tr("App", "   • Parágrafos: {valor}\n").format(valor=num_paragrafos))
        bloco_estatisticas.append(tr("App", "   • Nível hierárquico: {valor}\n").format(valor=nivel))
        bloco_estatisticas.append(tr("App", "   • Tipo: {valor}\n").format(valor=tipo_no))
        bloco_estatisticas.append("━" * 60)
        info_associadas.append("".join(bloco_estatisticas))

    filhos = hierarquia.get('filhos', [])
    if filhos:
        bloco_estrutura = []
        bloco_estrutura.append(
            tr("App", "\n🌿 SUB-SEÇÕES ({quantidade}):\n").format(quantidade=len(filhos))
        )

        for idx, filho in enumerate(filhos[:15], 1):
            titulo_filho = filho.get('titulo', tr("App", "Sem título"))[:50]
            num_conceitos_filho = len(filho.get('conceitos', []))
            num_ideias_filho = len(filho.get('ideias_principais', []))

            bloco_estrutura.append(
                tr("App", "   {idx}. {titulo} ({conceitos} conceitos, {ideias} ideias)\n").format(
                    idx=idx,
                    titulo=titulo_filho,
                    conceitos=num_conceitos_filho,
                    ideias=num_ideias_filho
                )
            )

        info_associadas.append("".join(bloco_estrutura))

    return info_associadas


def _montar_info_folha(tr: Callable[[str, str], str], ideia: Dict, numero: int, titulo_pai: str) -> List[str]:
    info_folha: List[str] = []

    texto_ideia = ideia.get('texto', '')

    bloco_header = []
    bloco_header.append(tr("App", "💡 IDEIA PRINCIPAL #{numero}\n").format(numero=numero))
    bloco_header.append("━" * 60)
    info_folha.append("".join(bloco_header))

    importancia = float(ideia.get('importancia', 0.0))
    bloco_importancia = []
    bloco_importancia.append(tr("App", "\n📊 Importância: {importancia:.2f} ").format(importancia=importancia))
    bloco_importancia.append("█" * int(importancia * 10) + "\n")
    bloco_importancia.append("━" * 60)
    info_folha.append("".join(bloco_importancia))

    bloco_localizacao = []
    bloco_localizacao.append(tr("App", "\n📍 LOCALIZAÇÃO:\n"))
    bloco_localizacao.append(tr("App", "   • Parágrafo: {valor}\n").format(valor=ideia.get('paragrafo', 'N/A')))
    bloco_localizacao.append(tr("App", "   • Posição na sentença: {valor}\n").format(valor=ideia.get('posicao_sentenca', 'N/A')))
    bloco_localizacao.append("━" * 60)
    info_folha.append("".join(bloco_localizacao))

    bloco_texto = []
    bloco_texto.append(tr("App", "\n💬 TEXTO COMPLETO:\n\n"))
    bloco_texto.append(tr("App", "\"{texto}\"\n").format(texto=texto_ideia))
    bloco_texto.append("━" * 60)
    info_folha.append("".join(bloco_texto))

    bloco_vinculo = []
    bloco_vinculo.append(tr("App", "\n🔗 Pertence a: {titulo}\n").format(titulo=(titulo_pai or "")[:40]))
    info_folha.append("".join(bloco_vinculo))

    return info_folha


def _gerar_mapa_de_hierarquia(self, hierarquia: Dict, x=0, y=0, nivel=0, pai=None):
    try:
        tr = QCoreApplication.translate

        cores_nivel = [
            QColor("#8B4513"),  # 0  Tronco (Documento) - marrom
            QColor("#A0522D"),  # 1  sienna
            QColor("#CD853F"),  # 2  peru
            QColor("#D2B48C"),  # 3  tan
            QColor("#1B5E20"),  # 4  verde bem escuro
            QColor("#2E7D32"),  # 5
            QColor("#388E3C"),  # 6
            QColor("#43A047"),  # 7
            QColor("#4CAF50"),  # 8
            QColor("#66BB6A"),  # 9
            QColor("#81C784"),  # 10
            QColor("#A5D6A7"),  # 11
            QColor("#C8E6C9"),  # 12
            QColor("#0D47A1"),  # 13 azul profundo
            QColor("#1565C0"),  # 14
            QColor("#1976D2"),  # 15
            QColor("#1E88E5"),  # 16
            QColor("#42A5F5"),  # 17
            QColor("#90CAF9"),  # 18
            QColor("#4A148C"),  # 19 roxo profundo
            QColor("#6A1B9A"),  # 20
            QColor("#7B1FA2"),  # 21
            QColor("#8E24AA"),  # 22
            QColor("#AB47BC"),  # 23
            QColor("#CE93D8"),  # 24
            QColor("#F9A825"),  # 25 amarelo/âmbar
            QColor("#FBC02D"),  # 26
            QColor("#FFD54F"),  # 27
            QColor("#FFE082"),  # 28
            QColor("#FFD700"),  # 29 folhas (Ideias) - dourado
            QColor("#D84315"),  # 30 laranja queimado
            QColor("#FF6F00"),  # 31
            QColor("#FF8F00"),  # 32
            QColor("#FFB300"),  # 33
            QColor("#B71C1C"),  # 34 vermelho profundo
            QColor("#C62828"),  # 35
            QColor("#E53935"),  # 36
            QColor("#EF5350"),  # 37
        ]

        titulo_key = hierarquia.get("titulo_key")
        if titulo_key:
            titulo = tr("App", titulo_key)

        else:
            titulo = hierarquia.get('titulo', tr("App", "Conceito"))

        tipo_no = hierarquia.get('tipo', 'secao')

        if nivel < len(cores_nivel):
            cor_no = cores_nivel[nivel]

        else:
            hue = (nivel * 37) % 360
            cor_no = QColor.fromHsv(hue, 150, 230)

        escala = max(1.2 - (nivel * 0.15), 0.5)
        no_principal = NoConceito(x, y, titulo, cor_no)
        no_principal.setScale(escala)
        self.scene.addItem(no_principal)
        self.nos.append(no_principal)

        no_principal._lumen_hierarquia_payload = hierarquia
        no_principal._lumen_hierarquia_nivel = nivel
        no_principal._lumen_hierarquia_tipo = tipo_no

        if pai is None:
            self._hierarquia_parent[no_principal] = None

        else:
            self._hierarquia_parent[no_principal] = pai
            self._hierarquia_children.setdefault(pai, []).append(no_principal)

        self._hierarquia_children.setdefault(no_principal, [])

        if pai:
            linha = LinhaConexao(pai, no_principal)
            espessura = max(4 - nivel, 1)
            linha.setPen(QPen(QColor(101, 67, 33), espessura))
            self.scene.addItem(linha)

        no_principal.info_associada = _montar_info_associadas(tr, hierarquia, nivel, tipo_no)
        no_principal._badge.setVisible(True)

        ideias = hierarquia.get('ideias_principais', [])
        if ideias and nivel >= 2:
            import math
            num_ideias = len(ideias)
            raio_ideias = 120
            angulo_base = 0 if not pai else (x - (pai.scenePos().x() if pai else 0))

            cor_folha = QColor("#FFD700")

            for idx, ideia in enumerate(ideias[:6]):
                angulo = angulo_base + (idx - num_ideias/2) * (180 / max(num_ideias, 1))
                x_ideia = x + raio_ideias * math.cos(math.radians(angulo))
                y_ideia = y + raio_ideias * math.sin(math.radians(angulo))

                texto_ideia = ideia.get('texto', '')
                texto_resumido = texto_ideia[:50] + "..." if len(texto_ideia) > 50 else texto_ideia

                no_ideia = NoConceito(x_ideia, y_ideia, f"💡 {texto_resumido}", cor_folha)
                no_ideia.setScale(0.7)

                no_ideia._lumen_ideia_payload = ideia
                no_ideia._lumen_ideia_numero = idx + 1
                no_ideia._lumen_ideia_parent_title = titulo

                self._hierarquia_parent[no_ideia] = no_principal
                self._hierarquia_children.setdefault(no_principal, []).append(no_ideia)
                self._hierarquia_children.setdefault(no_ideia, [])

                no_ideia.info_associada = _montar_info_folha(tr, ideia, idx + 1, titulo)
                no_ideia._badge.setVisible(True)

                self.scene.addItem(no_ideia)
                self.nos.append(no_ideia)

                linha_folha = LinhaConexao(no_principal, no_ideia)
                linha_folha.setPen(QPen(QColor(34, 139, 34, 150), 1, Qt.DashLine))
                self.scene.addItem(linha_folha)

                logger.debug(f"✓ Folha visual criada: '{texto_resumido}' para '{titulo[:30]}'")

        filhos = hierarquia.get('filhos', [])
        if filhos:
            import math

            raio_base = 250
            raio = raio_base + (nivel * 60)

            if pai:
                angulo_pai = math.atan2(y - pai.scenePos().y(), x - pai.scenePos().x())
                offset_angular = math.degrees(angulo_pai)

            else:
                offset_angular = -90

            abertura = 120 if nivel == 0 else 90
            angulo_inicio = offset_angular - (abertura / 2)
            angulo_step = abertura / max(len(filhos), 1)

            for i, filho in enumerate(filhos):
                angulo = angulo_inicio + (i * angulo_step)
                x_filho = x + raio * math.cos(math.radians(angulo))
                y_filho = y + raio * math.sin(math.radians(angulo))

                self._gerar_mapa_de_hierarquia(filho, x_filho, y_filho, nivel + 1, pai=no_principal)

        return no_principal

    except Exception as e:
        logger.error(f"Erro ao gerar mapa hierárquico: {e}", exc_info=True)
        return None
