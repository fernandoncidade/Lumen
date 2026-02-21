from source.utils.LogManager import LogManager
from source.modules.mapa.mp_04_ProcessadorIA import ProcessadorIA

logger = LogManager.get_logger()

def reorganizar_com_ia(self):
    try:
        if not self.nos:
            logger.warning("Nenhum conceito para reorganizar")
            return

        if self._hierarquia_root is not None and isinstance(self._hierarquia_children, dict) and self._hierarquia_children:
            idx_por_no = {no: i for i, no in enumerate(self.nos)}

            raiz_idx = idx_por_no.get(self._hierarquia_root, 0)

            filhos_idx = {i: [] for i in range(len(self.nos))}
            for pai_no, lista_filhos in self._hierarquia_children.items():
                pai_i = idx_por_no.get(pai_no)
                if pai_i is None:
                    continue

                for filho_no in (lista_filhos or []):
                    fi = idx_por_no.get(filho_no)
                    if fi is None:
                        continue

                    filhos_idx[pai_i].append(fi)

            niveis = {raiz_idx: 0}
            fila = [raiz_idx]
            visitados = {raiz_idx}
            while fila:
                atual = fila.pop(0)
                for viz in filhos_idx.get(atual, []):
                    if viz in visitados:
                        continue

                    visitados.add(viz)
                    niveis[viz] = niveis[atual] + 1
                    fila.append(viz)

            for i in range(len(self.nos)):
                if i not in visitados:
                    filhos_idx.setdefault(raiz_idx, []).append(i)
                    niveis[i] = 1

            hierarquia_existente = {
                "raiz": raiz_idx,
                "filhos": filhos_idx,
                "niveis": niveis,
                "pais": {}
            }

            self._aplicar_layout_arvore(hierarquia_existente)
            self._atualizar_visibilidade_linhas()

            if hasattr(self.view, "animate_focus_on") and self._hierarquia_root is not None:
                self.view.animate_focus_on(self._hierarquia_root)

            logger.info("Mapa reorganizado preservando a hierarquia existente (PDF)")
            return

        if self.processador_ia is None:
            self.processador_ia = ProcessadorIA()

        textos = [no.texto for no in self.nos]
        texto_completo = ". ".join(textos)

        doc = self.processador_ia.nlp(texto_completo)
        conceitos = self.processador_ia._extrair_conceitos_tfidf(doc, texto_completo)
        relacoes = self.processador_ia._identificar_relacoes_avancadas(doc, conceitos)
        conexoes_existentes = self._obter_conexoes_existentes()
        hierarquia = self._construir_hierarquia(conexoes_existentes)

        self._aplicar_layout_arvore(hierarquia)
        self._criar_relacoes_ia(relacoes)
        self._configurar_hierarquia_por_indices(hierarquia)

        if self.nos and hasattr(self.view, "animate_focus_on"):
            self.view.animate_focus_on(self.nos[hierarquia.get("raiz", 0)] if hierarquia else self.nos[0])

        logger.info("Mapa reorganizado em formato de árvore com sucesso")

    except Exception as e:
        logger.error(f"Erro ao reorganizar com IA: {str(e)}", exc_info=True)
