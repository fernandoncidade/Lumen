from __future__ import annotations
from typing import Dict, Iterator, List, Tuple
from PySide6.QtWidgets import QFileDialog, QProgressDialog
from PySide6.QtCore import Qt, QCoreApplication, QThread, QObject, Signal, Slot, QMetaObject
from source.utils.LogManager import LogManager

logger = LogManager.get_logger()


class _ImportWorker(QObject):
    progress_text = Signal(str)
    progress_value = Signal(int)
    progress_busy = Signal(bool)
    finished = Signal(object, object, object)
    error = Signal(str)

    def __init__(self, caminho: str, proc_existente=None):
        super().__init__()
        self.caminho = caminho
        self.proc_existente = proc_existente
        self._cancel = False

    def _cancelled(self) -> bool:
        try:
            if self._cancel:
                return True

            th = QThread.currentThread()
            return bool(th and th.isInterruptionRequested())

        except Exception:
            return self._cancel

    @Slot()
    def cancel(self):
        self._cancel = True

    def _emit_step(self, pct: int, label: str):
        self.progress_busy.emit(False)
        self.progress_value.emit(max(0, min(100, int(pct))))
        self.progress_text.emit(label)

    def _iter_nodes(self, root: Dict) -> Iterator[Dict]:
        stack = [root]
        while stack:
            n = stack.pop()
            yield n
            filhos = n.get("filhos", []) or []
            for f in reversed(filhos):
                stack.append(f)

    def _processar_nos_com_progresso(self, proc, arvore: Dict, idioma: str, pct_inicio: int, pct_fim: int,) -> None:
        nodes = list(self._iter_nodes(arvore))
        total = len(nodes)

        jobs: List[Tuple[int, Dict, str]] = []
        for idx, no in enumerate(nodes):
            texto_puro = (no.get("texto_puro") or "").strip()
            if texto_puro and len(texto_puro) > 50:
                jobs.append((idx, no, texto_puro[:1_000_000]))

            else:
                no["conceitos"] = []
                no["ideias_principais"] = []
                no["resumo_contextual"] = ""

        if self._cancelled():
            return

        if not jobs:
            self._emit_step(pct_fim, QCoreApplication.translate("App", "Processamento de nós concluído"))
            return

        pipe = getattr(getattr(proc, "nlp", None), "pipe", None)
        can_pipe = callable(pipe)

        batch_size = 8
        textos = [t for (_, _, t) in jobs]

        docs_iter = None
        try:
            if can_pipe:
                docs_iter = proc.nlp.pipe(textos, batch_size=batch_size, n_process=1)

            else:
                docs_iter = (proc.nlp(t) for t in textos)

        except Exception:
            docs_iter = (proc.nlp(t) for t in textos)

        for j, (doc_no, (orig_idx, no, texto_no)) in enumerate(zip(docs_iter, jobs), start=1):
            if self._cancelled():
                return

            nivel = int(no.get("nivel", 0) or 0)
            titulo = str(no.get("titulo", "Nó") or "Nó")

            try:
                no["conceitos"] = proc._extrair_conceitos_semanticos(doc_no, texto_no, nivel)
                no["ideias_principais"] = proc._extrair_ideias_principais(doc_no, texto_no, nivel)
                no["resumo_contextual"] = proc._gerar_resumo_contextual(doc_no, texto_no, nivel, titulo, idioma)

            except Exception as e:
                logger.warning(f"Falha ao processar nó '{titulo[:60]}' (nível {nivel}): {e}", exc_info=True)
                no["conceitos"] = no.get("conceitos", []) or []
                no["ideias_principais"] = no.get("ideias_principais", []) or []
                no["resumo_contextual"] = no.get("resumo_contextual", "") or ""

            frac = j / max(len(jobs), 1)
            pct = pct_inicio + int((pct_fim - pct_inicio) * frac)
            self._emit_step(
                pct,
                QCoreApplication.translate("App", "Processando nó {atual}/{total}: {titulo}").format(
                    atual=j,
                    total=len(jobs),
                    titulo=titulo[:60],
                ),
            )

    @Slot()
    def run(self):
        try:
            from source.modules.mapa.mp_04_ProcessadorIA import ProcessadorIA

            self._emit_step(0, QCoreApplication.translate("App", "Preparando importação..."))

            self._emit_step(5, QCoreApplication.translate("App", "Carregando modelo de IA..."))
            proc = self.proc_existente if self.proc_existente is not None else None
            if proc is None:
                proc = ProcessadorIA()

            else:
                self.progress_text.emit(QCoreApplication.translate("App", "Usando modelo já carregado"))

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(15, QCoreApplication.translate("App", "Extraindo texto..."))
            texto = proc.extrair_texto(self.caminho) or ""

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            if not texto.strip():
                self._emit_step(100, QCoreApplication.translate("App", "Documento vazio"))
                self.finished.emit({}, texto, proc)
                return

            self._emit_step(25, QCoreApplication.translate("App", "Detectando idioma..."))
            try:
                idioma = proc._detectar_idioma_texto(texto)

            except Exception:
                idioma = getattr(proc, "idioma_detectado", "pt")

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(35, QCoreApplication.translate("App", "Detectando seções..."))
            secoes_raw = proc._detectar_secoes_avancado(texto, idioma) or []

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(45, QCoreApplication.translate("App", "Construindo árvore hierárquica..."))
            arvore = proc._construir_arvore_hierarquica(texto, secoes_raw) or {}

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(46, QCoreApplication.translate("App", "Processando nós (NLP)..."))
            self._processar_nos_com_progresso(proc, arvore, idioma, pct_inicio=46, pct_fim=85)

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(90, QCoreApplication.translate("App", "Refinando com TF-IDF..."))
            try:
                proc._aplicar_tfidf_global(texto, arvore)

            except Exception as e:
                logger.debug(f"TF-IDF global falhou: {e}")

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(95, QCoreApplication.translate("App", "Identificando relações semânticas..."))
            try:
                rels = proc._identificar_relacoes_semanticas(arvore) or []
                arvore["relacoes"] = rels

            except Exception as e:
                logger.debug(f"Relações semânticas falharam: {e}")
                arvore.setdefault("relacoes", [])

            if self._cancelled():
                self.progress_text.emit(QCoreApplication.translate("App", "Cancelado"))
                return

            self._emit_step(98, QCoreApplication.translate("App", "Finalizando..."))
            try:
                proc._log_estrutura_completa(arvore)

            except Exception:
                pass

            self._emit_step(100, QCoreApplication.translate("App", "Concluído"))
            self.finished.emit(arvore, texto, proc)

        except Exception as e:
            logger.error(f"Erro no worker de importação: {e}", exc_info=True)
            self.error.emit(str(e))


class _UiBridge(QObject):
    def __init__(self, owner, progress: QProgressDialog, thread: QThread, worker: _ImportWorker, arquivo: str):
        super().__init__(owner)
        self._owner = owner
        self._progress = progress
        self._thread = thread
        self._worker = worker
        self._arquivo = arquivo

    @Slot(str)
    def set_label(self, txt: str):
        try:
            self._progress.setLabelText(txt)

        except Exception:
            pass

    @Slot(int)
    def set_value(self, v: int):
        try:
            self._progress.setRange(0, 100)
            self._progress.setValue(max(0, min(100, int(v))))

        except Exception:
            pass

    @Slot(bool)
    def set_busy(self, busy: bool):
        try:
            self._progress.setRange(0, 0 if busy else 100)

        except Exception:
            pass

    @Slot()
    def on_cancel(self):
        try:
            self._progress.setCancelButtonText(QCoreApplication.translate("App", "Cancelando..."))
            self._progress.setLabelText(QCoreApplication.translate("App", "Cancelando..."))

        except Exception:
            pass

        try:
            self._thread.requestInterruption()

        except Exception:
            pass

        try:
            QMetaObject.invokeMethod(self._worker, "cancel", Qt.QueuedConnection)

        except Exception:
            try:
                self._worker.cancel()

            except Exception:
                pass

    @Slot(str)
    def on_error(self, msg: str):
        logger.error(f"Erro ao importar documento (worker): {msg}")
        self._cleanup()

    @Slot(object, object, object)
    def on_finished(self, arvore, texto, proc):
        try:
            try:
                self._owner.processador_ia = proc

            except Exception:
                pass

            if not texto or not str(texto).strip():
                logger.warning("Documento vazio ou não pôde ser lido")
                return

            self._owner.limpar_mapa()

            self._owner._hierarquia_parent = {}
            self._owner._hierarquia_children = {}
            self._owner._modo_navegacao_hierarquia = False
            self._owner._hierarquia_root = None

            self._owner._lumen_layout_freeze_on_click = False
            self._owner._lumen_layout_orientation = "vertical"

            raiz_no = self._owner._gerar_mapa_de_hierarquia(arvore)
            if raiz_no:
                self._owner._habilitar_navegacao_hierarquia(raiz_no)

            logger.info(f"Mapa mental gerado com sucesso de: {self._arquivo}")

        except Exception as e:
            logger.error(f"Erro ao gerar mapa na finalização: {e}", exc_info=True)

        finally:
            self._cleanup()

    def _cleanup(self):
        try:
            self._progress.close()

        except Exception:
            pass

        try:
            if getattr(self._owner, "_lumen_import_thread", None) is self._thread:
                self._owner._lumen_import_thread = None

            if getattr(self._owner, "_lumen_import_worker", None) is self._worker:
                self._owner._lumen_import_worker = None

            if getattr(self._owner, "_lumen_import_bridge", None) is self:
                self._owner._lumen_import_bridge = None

        except Exception:
            pass

        try:
            self._thread.quit()
            self._thread.wait(6000)

        except Exception:
            pass

        try:
            self._worker.deleteLater()

        except Exception:
            pass

        try:
            self._thread.deleteLater()

        except Exception:
            pass

        try:
            self.deleteLater()

        except Exception:
            pass

def importar_documento_ia(self):
    try:
        arquivo, _ = QFileDialog.getOpenFileName(
            self,
            QCoreApplication.translate("App", "Importar Documento"),
            getattr(self, "caminho_persistente", ""),
            QCoreApplication.translate("App", "Documentos (*.pdf *.docx *.txt)")
        )

        if not arquivo:
            return

        t_prev = getattr(self, "_lumen_import_thread", None)
        w_prev = getattr(self, "_lumen_import_worker", None)
        if isinstance(t_prev, QThread) and t_prev.isRunning():
            try:
                t_prev.requestInterruption()

            except Exception:
                pass

            try:
                if w_prev is not None and hasattr(w_prev, "cancel"):
                    QMetaObject.invokeMethod(w_prev, "cancel", Qt.QueuedConnection)

            except Exception:
                pass

        progress = QProgressDialog(
            QCoreApplication.translate("App", "Preparando importação..."),
            QCoreApplication.translate("App", "Cancelar"),
            0,
            100,
            self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setWindowTitle(QCoreApplication.translate("App", "Lúmen"))
        progress.setMinimumDuration(0)
        progress.setAutoClose(False)
        progress.setAutoReset(False)
        progress.setValue(0)
        progress.show()

        thread = QThread(self)
        worker = _ImportWorker(arquivo, getattr(self, "processador_ia", None))
        worker.moveToThread(thread)

        bridge = _UiBridge(self, progress, thread, worker, arquivo)

        self._lumen_import_thread = thread
        self._lumen_import_worker = worker
        self._lumen_import_bridge = bridge

        thread.started.connect(worker.run)
        worker.progress_text.connect(bridge.set_label, Qt.QueuedConnection)
        worker.progress_value.connect(bridge.set_value, Qt.QueuedConnection)
        worker.progress_busy.connect(bridge.set_busy, Qt.QueuedConnection)
        worker.finished.connect(bridge.on_finished, Qt.QueuedConnection)
        worker.error.connect(bridge.on_error, Qt.QueuedConnection)
        progress.canceled.connect(bridge.on_cancel, Qt.QueuedConnection)

        thread.start()

    except Exception as e:
        logger.error(f"Erro ao importar documento com IA: {str(e)}", exc_info=True)
        try:
            progress.close()

        except Exception:
            pass
