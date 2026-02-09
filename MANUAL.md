# Manual de Utilização — Lúmen

<p align="center">
  <b>Selecione o idioma / Select language:</b><br>
  <a href="#ptbr">🇧🇷 Português (BR)</a> |
  <a href="#enus">🇺🇸 English (US)</a>
</p>

---

## <a id="ptbr"></a>🇧🇷 Português (BR)

<details>
<summary>Clique para expandir o manual em Português</summary>

# Manual de Utilização — Lúmen (PT‑BR)

> Este manual descreve como operar o aplicativo Lúmen (modo de uso), cobrindo funcionalidades, atalhos, fluxo de trabalho sugerido, resolução de problemas e informações sobre persistência de dados. Não é um guia de desenvolvimento.

## Índice
- [Visão Geral](#visão-geral)
- [Requisitos básicos (usuário)](#requisitos-básicos-usuário)
- [Como iniciar o aplicativo](#como-iniciar-o-aplicativo)
- [Abertura e controles globais](#abertura-e-controles-globais)
- [Atalhos globais úteis (padrões)](#atalhos-globais-úteis-padrões)
- [Módulos (índice por aba)]
  - [Leitor Acessível — Aba 1](#leitor-acessível---aba-1)
  - [Gestão de Tempo — Aba 2](#gestão-de-tempo---aba-2)
  - [Mapas Mentais — Aba 3](#mapas-mentais---aba-3)
  - [Método Feynman — Aba 4](#método-feynman---aba-4)
  - [Matriz de Eisenhower — Aba 5](#matriz-de-eisenhower---aba-5)
- [Menus e ações rápidas](#menus-e-ações-rápidas)
- [Sugestões de uso combinadas](#sugestões-de-uso-combinadas)
- [Solução de problemas (Troubleshooting)](#solução-de-problemas-troubleshooting)
- [Logs e diagnóstico](#logs-e-diagnóstico)
- [Armazenamento / Arquivos persistentes (resumo)](#armazenamento--arquivos-persistentes-resumo)
- [Exportar manual para PDF (opcional)](#exportar-manual-para-pdf-opcional)
- [Boas práticas de uso](#boas-práticas-de-uso)
- [Resumo rápido de atalhos](#resumo-rápido-de-atalhos)
- [FAQ](#perguntas-frequentes-faq)
- [Como obter ajuda / suporte](#como-obter-ajuda--suporte)

---

## Visão Geral
Lúmen é uma suíte de ferramentas para estudo composta por módulos principais: Leitor Acessível, Gestão de Tempo (Pomodoro + Gerenciador de Tarefas), Mapas Mentais, Método Feynman e Matriz de Eisenhower. A interface é organizada em abas; cada aba contém controles e ferramentas específicas ao módulo.

## Requisitos básicos (usuário)
- Windows (testado). Linux/macOS podem funcionar se dependências instaladas.
- Python 3.8+ para execução local.
- Conexão à Internet para Edge TTS (opcional).

## Como iniciar o aplicativo
No PowerShell (Windows):
```powershell
python main.py
```

## Abertura e controles globais
Ao abrir o Lúmen verá a janela principal com abas e uma barra de menus (Arquivo, Configurações, Idiomas, Vozes, Sobre). A barra de status exibe informações contextuais.

## Atalhos globais úteis (padrões)
- Ctrl+1 … Ctrl+5 — alternar abas (Leitor → Tempo → Mapa → Feynman → Eisenhower)  
- Ctrl+Q — sair  
- F1 — ajuda

---

## Módulos (detalhados por aba)

### Leitor Acessível — Aba 1
<a id="leitor-acessível---aba-1"></a>

<details>
<summary>Resumo rápido — Leitor Acessível (clique para expandir/recolher)</summary>

Conteúdo: carregamento de PDFs, extração de texto, TTS (Edge ou local), controle de velocidade/volume, régua de foco e formatações de texto.

</details>

<details>
<summary>Descrição completa — Leitor Acessível</summary>

Principais ações
- Carregar PDF: diálogo para selecionar PDF; texto extraído é exibido na área de leitura.
- Play / ▶️ Ler: inicia a leitura por TTS.
- Pausar / ⏸️ e Continuar: alterna o estado da leitura.
- Stop / ⏹️: finaliza a leitura e limpa a fila de áudio.

Controles e opções
- Velocidade (slider): ajusta a velocidade do TTS.
- Volume (slider): ajusta volume do player interno.
- Fonte (combo): altera tamanho e tipo de fonte do texto exibido.
- Botões de edição: Novo, Salvar Como, marcadores, recuos e alinhamentos.

PDF — barra de ferramentas
- Navegação por página: Primeira / Anterior / Próxima / Última + entrada numérica.
- Zoom: 50%, 100%, Ajustar à largura, Ajustar à página.
- Modos: página única ou rolagem contínua.
- Hand Mode: arraste o PDF com o mouse.

Régua de Foco
- Ativar/Desativar via botão.
- Mover/Redimensionar: arraste; ajuste fino com setas; ESC fecha.
- Sincroniza com menu principal.

Vozes e TTS
- Mecanismos: Edge TTS (neural, internet) e motores locais (pyttsx3).
- Seleção de voz no menu Vozes; pode ser persistida.
- Recomendações: Edge TTS para voz natural; fallback local em caso de falha.

Observações de acessibilidade
- Use tamanhos de fonte maiores e contraste alto para melhor legibilidade.
- Ative régua de foco para leitura linha-a-linha.

</details>

---

### Gestão de Tempo — Aba 2
<a id="gestão-de-tempo---aba-2"></a>

<details>
<summary>Resumo rápido — Gestão de Tempo (Pomodoro + Kanban)</summary>

Conteúdo: temporizador Pomodoro configurável, gerenciador de tarefas estilo Kanban, registro de pomodoros e integração entre timer e tarefas.

</details>

<details>
<summary>Descrição completa — Gestão de Tempo</summary>

Pomodoro
- Controles: Iniciar / Pausar / Resetar / Pular ciclo.
- Ciclos: foco, descanso curto, descanso longo.
- Ao fim do ciclo: alerta sonoro e opção de marcar pomodoro na tarefa atual.

Gerenciador de Tarefas (Kanban)
- Adicionar tarefa: título, prioridade, descrição e estimativa de pomodoros.
- Colunas típicas: Todo, Doing, Done.
- Operações: mover, editar, remover, menu de contexto.
- Persistência: tarefas armazenadas em JSON no diretório de dados do app.

Fluxo sugerido
1. Criar tarefas em Todo.  
2. Mover tarefa para Doing quando iniciar foco.  
3. Iniciar Pomodoro vinculado à tarefa.

</details>

---

### Mapas Mentais — Aba 3
<a id="mapas-mentais---aba-3"></a>

<details>
<summary>Resumo rápido — Mapas Mentais</summary>

Editor visual de nós e ligações, edição por duplo clique, exportação para imagem e salvamento de projeto.

</details>

<details>
<summary>Descrição completa — Mapas Mentais</summary>

Criar e editar mapas
- Adicionar nó: cria um conceito.
- Conectar nós: modo conexão, clique origem → destino.
- Editar nó: duplo clique para texto/nota/cor.
- Arrastar: reposicionamento livre.

Salvar / Exportar
- Salvar projeto: mantém estrutura e posições.
- Exportar PNG: gera imagem do mapa.
- Recomendações: salvamentos frequentes e exportação antes de grandes alterações.

</details>

---

### Método Feynman — Aba 4
<a id="método-feynman---aba-4"></a>

<details>
<summary>Resumo rápido — Método Feynman</summary>

Ferramenta para explicar conceitos com etapas: explicação simples, lacunas, revisão e avaliação de domínio.

</summary>

</details>

<details>
<summary>Descrição completa — Método Feynman</summary>

Fluxo básico
- Novo Conceito: cria entrada com campos Título, Explicação Simples, Pontos de Dúvida, Resumo Revisado e Nível de Domínio.
- Salvar Conceito: persiste em arquivo; lista de conceitos à esquerda.
- Deletar: remove conceito selecionado.

Como usar
1. Escolha um conceito.
2. Explique em linguagem simples.
3. Identifique lacunas e revise.
4. Atualize o resumo e registre o nível de domínio.

Integração
- Vincule nós do mapa mental a conceitos do Feynman para revisão iterativa.

</details>

---

### Matriz de Eisenhower — Aba 5
<a id="matriz-de-eisenhower---aba-5"></a>

<details>
<summary>Resumo rápido — Matriz de Eisenhower</summary>

Quadro de priorização com quatro quadrantes; suporte a data/hora, calendário e exportação simples.

</details>

<details>
<summary>Descrição completa — Matriz de Eisenhower</summary>

Adicionar e organizar tarefas
- Campo: título + opcional data/hora.
- Seletor de quadrante: Importante/Urgente, Importante/Não Urgente, Não Importante/Urgente, Não Importante/Não Urgente.
- Marcar concluído, editar e mover entre quadrantes.

Recursos extras
- Visualização por horário: painel calendário mostra distribuição por data/hora.
- Importar/Exportar: CSV/Excel (quando disponível no menu).

Fluxo sugerido
- Alocar backlog semanal nos quadrantes; priorizar pomodoros nas tarefas importantes.

</details>

---

## Menus e ações rápidas
- Arquivo: comandos para carregar/salvar projetos, exportar mapas, importar tarefas.
- Configurações: Idioma, Vozes, Fonte padrão.
- Idiomas: mudar idioma da interface e das strings de módulos.
- Ajuda: versão e documentação rápida.

## Sugestões de uso combinadas
- Leitura + Pomodoro: abra material no Leitor, ative régua de foco, vincule tarefa ao Pomodoro e inicie sessão.
- Mapas + Feynman: crie nós e registre explicações no Feynman para revisão.
- Eisenhower para priorizar semanalmente e planejar pomodoros.

## Solução de problemas (Troubleshooting)
- Sem som:
  - Verificar volume do sistema e do app.
  - Edge TTS: confirmar Internet.
  - pyttsx3: confirmar motor instalado.
- PDF sem texto:
  - PDF pode ser imagem (use OCR).
  - Verificar bibliotecas: pdfplumber, pypdf.
- Vozes não listadas:
  - Recarregar vozes ou reiniciar app.
- Erro ao salvar/ler:
  - Verificar permissões de pasta; localizar arquivos no diretório de dados.

## Logs e diagnóstico
- LogManager gera logs; verificar pasta de dados ou saída do terminal (`python main.py`).

## Armazenamento / Arquivos persistentes (resumo)
- Tarefas: JSON (ex.: tarefas.json).  
- Mapas: projeto (.map, .json).  
- Conceitos Feynman: conceitos.json.  
- Configurações: config.json.  
- Local sugerido: `%APPDATA%\Lumen` ou `%LOCALAPPDATA%\TEA_TDAH_Dislexia`.

## Exportar manual para PDF (opcional)
Com pandoc:
```powershell
pandoc MANUAL.md -o MANUAL.pdf --pdf-engine=xelatex
```
Ou use VS Code: "Markdown: Export (PDF)".

## Boas práticas de uso
- Salve mapas e conceitos regularmente.
- Faça backups periódicos.
- Mantenha app e dependências atualizados.

## Resumo rápido de atalhos
- Ctrl+1 … Ctrl+5 — trocar abas  
- Ctrl+O — abrir arquivo (PDF)  
- Ctrl+R — iniciar leitura  
- Ctrl+P — pausar leitura  
- Ctrl+T — adicionar tarefa  
- Ctrl+N — novo nó/conceito  
- Ctrl+Q — sair  
- F1 — ajuda

## Perguntas Frequentes (FAQ)
- Como deixar voz mais natural? Use Edge TTS (vozes neurais) e ajuste velocidade/volume.
- Onde meus dados são salvos? No diretório de dados do app (`%APPDATA%` / `~/.local/share`).

## Como obter ajuda / suporte
- Menu Ajuda para versão/documentação.
- Para problemas técnicos, anexe logs do LogManager ao abrir um issue.

</details>

---

## <a id="enus"></a>🇺🇸 English (US)

<details>
<summary>Click to expand the manual in English</summary>

# User Manual — Lúmen (EN‑US)

> This manual describes how to operate the Lúmen application (user mode), covering features, shortcuts, suggested workflows, troubleshooting and data persistence. Not a developer guide.

## Index
- [Overview](#overview)
- [Basic requirements (user)](#basic-requirements-user)
- [How to start the application](#how-to-start-the-application)
- [Main window and global controls](#main-window-and-global-controls)
- [Useful global shortcuts (default)](#useful-global-shortcuts-default)
- [Modules (tab index)]
  - [Accessible Reader — Tab 1](#accessible-reader---tab-1)
  - [Time Management — Tab 2](#time-management---tab-2)
  - [Mind Maps — Tab 3](#mind-maps---tab-3)
  - [Feynman Technique — Tab 4](#feynman-technique---tab-4)
  - [Eisenhower Matrix — Tab 5](#eisenhower-matrix---tab-5)
- [Menus and quick actions](#menus-and-quick-actions)
- [Combined workflows](#combined-workflows)
- [Troubleshooting](#troubleshooting)
- [Logs and diagnostics](#logs-and-diagnostics)
- [Storage / Persistent files (summary)](#storage--persistent-files-summary)
- [Export manual to PDF (optional)](#export-manual-to-pdf-optional)
- [Best practices](#best-practices)
- [Shortcuts quick reference](#shortcuts-quick-reference)
- [FAQ](#faq)
- [How to get help / support](#how-to-get-help--support)

---

## Overview
Lúmen is a study suite composed of main modules: Accessible Reader, Time Management (Pomodoro + Task Manager), Mind Maps, Feynman Technique and Eisenhower Matrix. The UI is tabbed; each tab exposes controls and tools for that module.

## Basic requirements (user)
- Windows (tested). Linux/macOS may work if dependencies are installed.
- Python 3.8+ for local run.
- Internet connection for Edge TTS (optional).

## How to start the application
In PowerShell (Windows):
```powershell
python main.py
```

## Main window and global controls
On launch you will see the main window with tabs and a menu bar (File, Settings, Languages, Voices, About). The status bar displays contextual info.

## Useful global shortcuts (default)
- Ctrl+1 … Ctrl+5 — switch tabs (Reader → Time → Map → Feynman → Eisenhower)  
- Ctrl+Q — quit  
- F1 — help

---

## Modules (detailed by tab)

### Accessible Reader — Tab 1
<a id="accessible-reader---tab-1"></a>

<details>
<summary>Quick summary — Accessible Reader</summary>

Features: PDF loading, text extraction, TTS (Edge or local), speed/volume controls, focus ruler and text formatting tools.

</details>

<details>
<summary>Full description — Accessible Reader</summary>

Main actions
- Load PDF: opens dialog to select PDF; extracted text displays in reader area.
- Play / ▶️ Read: starts TTS playback.
- Pause / ⏸️ and Resume: toggles playback state.
- Stop / ⏹️: ends reading and clears audio queue.

Controls and options
- Speed (slider): adjust TTS rate.
- Volume (slider): adjust player volume.
- Font (combo): change font family/size.
- Edit buttons: New, Save As, bullets, indent/align.

PDF toolbar
- Page navigation: First / Prev / Next / Last + numeric input.
- Zoom: 50%, 100%, Fit Width, Fit Page.
- Modes: single page or continuous scroll.
- Hand Mode: drag the PDF canvas.

Focus Ruler
- Toggle via button.
- Move/Resize: drag; fine tune with arrow keys; ESC closes.
- Syncs with main menu option.

Voices and TTS
- Engines: Edge TTS (neural, requires internet) and local engines (pyttsx3).
- Select voice in Voices menu; selection can be persisted.
- Recommendation: Edge TTS for more natural voices; fallback to local if unavailable.

Accessibility notes
- Use larger fonts and high contrast for readability.
- Use focus ruler for line‑by‑line reading.

</details>

---

### Time Management — Tab 2
<a id="time-management---tab-2"></a>

<details>
<summary>Quick summary — Time Management (Pomodoro + Kanban)</summary>

Features: configurable Pomodoro timer, Kanban-style task manager, pomodoro logging and timer-task integration.

</details>

<details>
<summary>Full description — Time Management</summary>

Pomodoro
- Controls: Start / Pause / Reset / Skip cycle.
- Cycles: work, short break, long break.
- End of cycle: sound alert and option to log pomodoro to the current task.

Task Manager (Kanban)
- Add task: title, priority, description, estimated pomodoros.
- Typical columns: Todo, Doing, Done.
- Actions: move, edit, remove, context menu.
- Persistence: tasks stored in JSON inside app data directory.

Suggested flow
1. Create tasks in Todo.  
2. Move task to Doing when starting focus.  
3. Start Pomodoro linked to the task.

</details>

---

### Mind Maps — Tab 3
<a id="mind-maps---tab-3"></a>

<details>
<summary>Quick summary — Mind Maps</summary>

Visual editor of nodes and connections, edit by double-click, export image and save project.

</details>

<details>
<summary>Full description — Mind Maps</summary>

Create and edit maps
- Add node: creates a concept.
- Connect nodes: connection mode, click source → destination.
- Edit node: double-click to edit text/notes/color.
- Drag: free positioning.

Save / Export
- Save project: preserves structure and positions.
- Export PNG: create an image of the map.
- Recommendations: save frequently and export before big changes.

</details>

---

### Feynman Technique — Tab 4
<a id="feynman-technique---tab-4"></a>

<details>
<summary>Quick summary — Feynman Technique</summary>

Tool to explain concepts in steps: simple explanation, gaps, review and mastery assessment.

</details>

<details>
<summary>Full description — Feynman Technique</summary>

Basic flow
- New Concept: creates an entry with Title, Simple Explanation, Points of Doubt, Reviewed Summary and Mastery Level.
- Save Concept: persisted to file; concept list on the left.
- Delete: removes selected concept.

How to use
1. Choose a concept.  
2. Explain in simple language.  
3. Identify gaps and revise.  
4. Update the summary and record mastery level.

Integration
- Link mind‑map nodes to Feynman concepts for iterative review.

</details>

---

### Eisenhower Matrix — Tab 5
<a id="eisenhower-matrix---tab-5"></a>

<details>
<summary>Quick summary — Eisenhower Matrix</summary>

Priority board with four quadrants; support for date/time, calendar view and simple export.

</details>

<details>
<summary>Full description — Eisenhower Matrix</summary>

Add and organize tasks
- Field: title + optional date/time.
- Quadrant selector: Important/Urgent, Important/Not Urgent, Not Important/Urgent, Not Important/Not Urgent.
- Mark complete, edit and move between quadrants.

Extra features
- Time view: calendar panel shows distribution by date/time.
- Import/Export: CSV/Excel where available in menu.

Suggested flow
- Allocate weekly backlog into quadrants; prioritize pomodoros for important tasks.

</details>

---

## Menus and quick actions
- File: commands to load/save projects, export maps, import tasks.
- Settings: Language, Voices, Default font.
- Languages: switch UI language and module strings.
- Help: version and quick documentation.

## Combined workflows
- Reader + Pomodoro: open material in Reader, enable focus ruler, link a task to Pomodoro and start a session.
- Mind Maps + Feynman: build nodes and record explanations in Feynman for review.
- Use Eisenhower to prioritize weekly work and plan pomodoros.

## Troubleshooting
- No audio:
  - Check system/app volume.
  - Edge TTS: verify internet connection.
  - pyttsx3: verify engine availability.
- PDF without text:
  - The PDF may be an image (use OCR).
  - Check libraries: pdfplumber, pypdf.
- Voices not listed:
  - Reload voices or restart the app.
- Errors saving/loading:
  - Check folder permissions; look in the app data directory.

## Logs and diagnostics
- LogManager writes logs; check app data folder or terminal output when running (`python main.py`).

## Storage / Persistent files (summary)
- Tasks: JSON (e.g., tasks.json).  
- Maps: project (.map, .json).  
- Feynman concepts: concepts.json.  
- Settings: config.json.  
- Suggested location: `%APPDATA%\Lumen` or `%LOCALAPPDATA%\TEA_TDAH_Dislexia`.

## Export manual to PDF (optional)
With pandoc:
```powershell
pandoc MANUAL.md -o MANUAL.pdf --pdf-engine=xelatex
```
Or use VS Code: "Markdown: Export (PDF)".

## Best practices
- Save maps and concepts frequently.
- Keep backups.
- Maintain app and dependencies up to date.

## Shortcuts quick reference
- Ctrl+1 … Ctrl+5 — switch tabs  
- Ctrl+O — open file (PDF)  
- Ctrl+R — start reading  
- Ctrl+P — pause reading  
- Ctrl+T — add task  
- Ctrl+N — new node/concept  
- Ctrl+Q — quit  
- F1 — help

## FAQ
- How to make voice more natural? Use Edge TTS (neural voices) and tune speed/volume.
- Where are my data saved? In the app data directory (`%APPDATA%` / `~/.local/share`).

## How to get help / support
- Help menu for version/documentation.
- For technical issues, attach LogManager logs when opening an issue.

</details>

---

Arquivo atualizado: `MANUAL.md` com versões em Português e Inglês e blocos expansíveis por seção.
