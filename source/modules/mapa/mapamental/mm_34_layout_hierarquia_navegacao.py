from __future__ import annotations
from typing import List, Optional, Tuple, Iterable, Set, Dict
from PySide6.QtCore import QPointF, QRectF
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()

def _resolver_sobreposicoes_global(self, nos: Optional[List[object]] = None, apenas_visiveis: bool = True, push_pad: float = 22.0, push_max_iters: int = 80, push_direcao: str = "down",):
    try:
        scene = getattr(self, "scene", None)

        def _snap(p: QPointF) -> QPointF:
            try:
                if scene is not None and hasattr(scene, "snap"):
                    return scene.snap(p)

            except Exception:
                pass

            return p

        def _x(no) -> float:
            return float(no.pos().x())

        def _y(no) -> float:
            return float(no.pos().y())

        def _rect_scene(no) -> QRectF:
            return no.mapToScene(no.boundingRect()).boundingRect()

        def _visiveis(lista: List) -> List:
            if not apenas_visiveis:
                return list(lista or [])

            return [n for n in (lista or []) if getattr(n, "isVisible", lambda: True)()]

        vis = _visiveis(nos if nos is not None else (getattr(self, "nos", []) or []))
        if not vis:
            return

        if push_direcao == "right":
            vis.sort(key=lambda n: (_x(n), _y(n)))

        else:
            vis.sort(key=lambda n: (_y(n), _x(n)))

        placed: List[Tuple[object, QRectF]] = []
        for no in vis:
            it = 0
            while it < push_max_iters:
                r = _rect_scene(no).adjusted(-push_pad, -push_pad, push_pad, push_pad)

                colidiu = None
                for (_, pr) in placed:
                    if r.intersects(pr):
                        colidiu = pr
                        break

                if colidiu is None:
                    placed.append((no, r))
                    break

                if push_direcao == "right":
                    dx = (colidiu.right() - r.left()) + (push_pad * 1.2)
                    no.setPos(_snap(QPointF(_x(no) + dx, _y(no))))

                else:
                    dy = (colidiu.bottom() - r.top()) + (push_pad * 1.2)
                    no.setPos(_snap(QPointF(_x(no), _y(no) + dy)))

                it += 1

            if it >= push_max_iters:
                r = _rect_scene(no).adjusted(-push_pad, -push_pad, push_pad, push_pad)
                placed.append((no, r))

        try:
            if scene is not None and hasattr(scene, "itemsBoundingRect"):
                br = scene.itemsBoundingRect()
                if not br.isNull() and not br.isEmpty():
                    padding = 1400
                    alvo = br.adjusted(-padding, -padding, padding, padding)
                    atual = scene.sceneRect()

                    if atual.isNull() or atual.isEmpty():
                        scene.setSceneRect(alvo)

                    else:
                        scene.setSceneRect(atual.united(alvo))

        except Exception:
            pass

    except Exception as e:
        logger.error(f"Erro ao resolver sobreposições globalmente: {e}", exc_info=True)

def calcular_larguras_obj(root, filhos_map: Dict[object, List[object]], espacamento_base: float, visiveis: Optional[Set[object]] = None) -> Dict[object, float]:
    try:
        H_MARGIN = 40.0
        GAP_INTER_FILHOS = max(espacamento_base * 0.1, 20.0)

        def rect_width(no) -> float:
            try:
                r: QRectF = no.mapToScene(no.boundingRect()).boundingRect()
                return max(r.width(), espacamento_base) + H_MARGIN

            except Exception:
                return espacamento_base + H_MARGIN

        larguras: Dict[object, float] = {}
        visited = set()

        def _rec(no):
            if no in visited:
                return larguras.get(no, espacamento_base)
            visited.add(no)

            filhos = (filhos_map.get(no, []) or [])
            if visiveis is not None:
                filhos = [f for f in filhos if f in visiveis]

            if not filhos:
                w = rect_width(no)
                larguras[no] = max(w, espacamento_base)
                return larguras[no]

            soma = 0.0
            for f in filhos:
                wf = _rec(f)
                soma += wf

            soma += max(0, (len(filhos) - 1)) * GAP_INTER_FILHOS
            own = rect_width(no)
            larguras[no] = max(own, soma, espacamento_base)
            return larguras[no]

        _rec(root)
        return larguras

    except Exception as e:
        logger.error(f"Erro em calcular_larguras_obj: {e}", exc_info=True)
        return {}

def posicionar_subarvore_obj(self, raiz, filhos_map: Dict[object, List[object]], larguras: Dict[object, float], x: float, y: float, espacamento_v: float):
    try:
        if raiz is None:
            return

        try:
            raiz.setPos(QPointF(x, y))
            if hasattr(self, "_expandir_area_se_necessario"):
                self._expandir_area_se_necessario(raiz)

        except Exception:
            pass

        filhos = (filhos_map.get(raiz, []) or [])
        if not filhos:
            return

        largura_total = sum(larguras.get(f, max(200.0, espacamento_v)) for f in filhos)
        GAP_MIN = max(espacamento_v * 0.1, 20.0)
        largura_total += GAP_MIN * max(0, (len(filhos) - 1))

        x_inicio = x - (largura_total / 2.0)

        alturas = []
        for f in filhos:
            try:
                r: QRectF = f.mapToScene(f.boundingRect()).boundingRect()
                alturas.append(r.height())

            except Exception:
                alturas.append(80.0)

        max_h = max(alturas) if alturas else 80.0
        espacamento_real_v = max(espacamento_v, max_h * 1.4)

        x_atual = x_inicio
        for filho in filhos:
            largura_f = larguras.get(filho, max(200.0, espacamento_v))
            x_filho = x_atual + (largura_f / 2.0)
            y_filho = y + espacamento_real_v

            try:
                posicionar_subarvore_obj(self, filho, filhos_map, larguras, x_filho, y_filho, espacamento_v)

            except Exception as e:
                logger.error(f"Erro ao posicionar subárvore do nó {filho}: {e}", exc_info=True)

            x_atual += largura_f + GAP_MIN

    except Exception as e:
        logger.error(f"Erro ao posicionar subárvore: {e}", exc_info=True)

def _layout_hierarquia_navegacao(self):
    try:
        if not getattr(self, "_modo_navegacao_hierarquia", False):
            return

        root = getattr(self, "_hierarquia_root", None)
        if root is None:
            return

        orient = str(getattr(self, "_lumen_layout_orientation", "vertical") or "vertical").lower()
        if orient not in ("vertical", "horizontal"):
            orient = "vertical"

        filhos_map = getattr(self, "_hierarquia_children", {}) or {}
        parent_map = getattr(self, "_hierarquia_parent", {}) or {}

        scene = getattr(self, "scene", None)

        DEPTH_SPACING = 180.0
        GAP_MAJOR = 55.0
        GAP_MINOR = 50.0
        SLOT_MARGIN = 70.0

        def _snap(p: QPointF) -> QPointF:
            try:
                if scene is not None and hasattr(scene, "snap"):
                    return scene.snap(p)

            except Exception:
                pass

            return p

        def _major(no) -> float:
            return float(no.pos().y() if orient == "horizontal" else no.pos().x())

        def _depth(no) -> float:
            return float(no.pos().x() if orient == "horizontal" else no.pos().y())

        def _set_pos(no, major_val: float, depth_val: float):
            if orient == "horizontal":
                no.setPos(_snap(QPointF(depth_val, major_val)))

            else:
                no.setPos(_snap(QPointF(major_val, depth_val)))

        def _rect_scene(no) -> QRectF:
            return no.mapToScene(no.boundingRect()).boundingRect()

        def _visiveis(nos: List) -> List:
            return [n for n in (nos or []) if getattr(n, "isVisible", lambda: True)()]

        def _posicionar_filhos(pai):
            filhos = _visiveis(filhos_map.get(pai, []))
            if not filhos:
                return

            vis_set = set(_visiveis(self.nos if hasattr(self, "nos") else []))
            larguras = calcular_larguras_obj(pai, filhos_map, espacamento_base=200.0, visiveis=vis_set)

            p = pai.pos()
            x = float(p.x())
            y = float(p.y())
            posicionar_subarvore_obj(self, pai, filhos_map, larguras, x, y, espacamento_v=DEPTH_SPACING)

        expandidos = list(getattr(self, "_nos_expandidos", set()) or set())
        for no in expandidos:
            _posicionar_filhos(no)

        if orient == "horizontal":
            _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="right")
            _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="down")

        else:
            _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="down")

        if hasattr(self, "_atualizar_visibilidade_linhas"):
            self._atualizar_visibilidade_linhas()

    except Exception as e:
        logger.error(f"Erro no layout da navegação hierárquica: {e}", exc_info=True)

def _layout_incremental_preservando_base(self, novos_visiveis: Set[object], fixos_visiveis: Set[object], removidos_visiveis: Set[object] | None = None):
    try:
        if not (novos_visiveis or (removidos_visiveis or set())):
            return

        if not getattr(self, "_modo_navegacao_hierarquia", False):
            return

        orient = str(getattr(self, "_lumen_layout_orientation", "vertical") or "vertical").lower()
        if orient not in ("vertical", "horizontal"):
            orient = "vertical"

        filhos_map = getattr(self, "_hierarquia_children", {}) or {}
        parent_map = getattr(self, "_hierarquia_parent", {}) or {}

        scene = getattr(self, "scene", None)

        DEPTH_SPACING = 180.0
        GAP_MAJOR = 55.0
        GAP_MINOR = 50.0
        SLOT_MARGIN = 70.0

        PUSH_PAD = 22.0
        PUSH_MAX_ITERS = 80

        def _snap(p: QPointF) -> QPointF:
            try:
                if scene is not None and hasattr(scene, "snap"):
                    return scene.snap(p)

            except Exception:
                pass

            return p

        def _rect_scene(no) -> QRectF:
            return no.mapToScene(no.boundingRect()).boundingRect()

        def _x(no) -> float:
            return float(no.pos().x())

        def _y(no) -> float:
            return float(no.pos().y())

        def _major(no) -> float:
            return float(_y(no) if orient == "horizontal" else _x(no))

        def _depth(no) -> float:
            return float(_x(no) if orient == "horizontal" else _y(no))

        def _set_pos(no, major_val: float, depth_val: float):
            if orient == "horizontal":
                no.setPos(_snap(QPointF(depth_val, major_val)))

            else:
                no.setPos(_snap(QPointF(major_val, depth_val)))

        def _visiveis(nos: Iterable[object]) -> List[object]:
            return [n for n in (list(nos) or []) if getattr(n, "isVisible", lambda: True)()]

        pais_afetados = set()
        conjunto_acao = set(novos_visiveis or set()) | set(removidos_visiveis or set())
        for n in conjunto_acao:
            p = parent_map.get(n)
            while p is not None:
                pais_afetados.add(p)
                p = parent_map.get(p)

        def _ancestral_depth(n):
            d = 0
            p = parent_map.get(n)
            while p is not None:
                d += 1
                p = parent_map.get(p)

            return d

        pais_afetados_list = sorted(list(pais_afetados), key=_ancestral_depth, reverse=False)

        vis_set_global = set(_visiveis(self.nos if hasattr(self, "nos") else []))
        for pai in pais_afetados_list:
            try:
                filhos_vis = _visiveis(filhos_map.get(pai, []))
                if not filhos_vis:
                    continue

                larguras = calcular_larguras_obj(pai, filhos_map, espacamento_base=200.0, visiveis=vis_set_global)

                p = pai.pos()
                x = float(p.x())
                y = float(p.y())
                posicionar_subarvore_obj(self, pai, filhos_map, larguras, x, y, espacamento_v=DEPTH_SPACING)

            except Exception as e:
                logger.error(f"Erro ao recalcular/reposicionar subárvore do pai {pai}: {e}", exc_info=True)

        try:
            if orient == "horizontal":
                anchor = getattr(self, "_hierarquia_root", None)
                anchor_pos = anchor.pos() if anchor is not None else QPointF(0, 0)

                nos_to_rotate = _visiveis(self.nos if hasattr(self, "nos") else [])
                for no in nos_to_rotate:
                    try:
                        p = no.pos()
                        rel = p - anchor_pos
                        swapped = QPointF(rel.y(), rel.x())
                        no.setPos(_snap(swapped + anchor_pos))
                        if hasattr(self, "_expandir_area_se_necessario"):
                            self._expandir_area_se_necessario(no)

                    except Exception:
                        pass

                try:
                    if orient == "horizontal":
                        _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="right")
                        _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="down")

                    else:
                        _resolver_sobreposicoes_global(self, nos=None, apenas_visiveis=True, push_direcao="down")

                except Exception:
                    pass

                mover = list(novos_visiveis)

                if hasattr(self, "_atualizar_visibilidade_linhas"):
                    self._atualizar_visibilidade_linhas()

        except Exception as e:
            logger.error(f"Erro ao aplicar rotação incremental (horizontal): {e}", exc_info=True)

        mover = list(novos_visiveis)
        if orient == "horizontal":
            mover.sort(key=lambda n: (_x(n), _y(n)))

        else:
            mover.sort(key=lambda n: (_y(n), _x(n)))

        placed: List[QRectF] = []
        obstaculos: List[QRectF] = []

        for f in fixos_visiveis:
            try:
                obstaculos.append(_rect_scene(f).adjusted(-PUSH_PAD, -PUSH_PAD, PUSH_PAD, PUSH_PAD))

            except Exception:
                pass

        for no in mover:
            it = 0
            while it < PUSH_MAX_ITERS:
                r = _rect_scene(no).adjusted(-PUSH_PAD, -PUSH_PAD, PUSH_PAD, PUSH_PAD)

                colidiu = None
                for pr in obstaculos:
                    if r.intersects(pr):
                        colidiu = pr
                        break

                if colidiu is None:
                    for pr in placed:
                        if r.intersects(pr):
                            colidiu = pr
                            break

                if colidiu is None:
                    placed.append(r)
                    break

                if orient == "horizontal":
                    dx = (colidiu.right() - r.left()) + (PUSH_PAD * 1.2)
                    no.setPos(_snap(QPointF(_x(no) + dx, _y(no))))

                else:
                    dy = (colidiu.bottom() - r.top()) + (PUSH_PAD * 1.2)
                    no.setPos(_snap(QPointF(_x(no), _y(no) + dy)))

                it += 1

            try:
                placed.append(_rect_scene(no).adjusted(-PUSH_PAD, -PUSH_PAD, PUSH_PAD, PUSH_PAD))

            except Exception:
                pass

        if hasattr(self, "_atualizar_visibilidade_linhas"):
            self._atualizar_visibilidade_linhas()

    except Exception as e:
        logger.error(f"Erro no incremental preservando base: {e}", exc_info=True)
