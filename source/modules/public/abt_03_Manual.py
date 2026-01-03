from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class ManualDetails:
    summary: str
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()


@dataclass(frozen=True)
class ManualSection:
    id: str
    title: str
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()
    details: tuple[ManualDetails, ...] = ()


@dataclass(frozen=True)
class ManualBlock:
    kind: str
    text: str = ""
    section_id: str | None = None


def normalize_language(lang: str | None) -> str:
    if not lang:
        return "pt_BR"

    v = lang.strip().replace("-", "_").lower()
    if v in ("pt_br", "pt"):
        return "pt_BR"

    if v in ("en_us", "en"):
        return "en_US"

    return "pt_BR"


def get_manual_title(lang: str | None = None) -> str:
    lang = normalize_language(lang)
    return "Manual de Utilização — Lúmen" if lang == "pt_BR" else "User Manual — Lúmen"


def get_manual_document(lang: str | None = None) -> tuple[ManualSection, ...]:
    lang = normalize_language(lang)
    return _DOC_EN_US if lang == "en_US" else _DOC_PT_BR


def get_manual_blocks(lang: str | None = None) -> tuple[tuple[ManualBlock, ...], Tuple[str, ...]]:
    lang = normalize_language(lang)
    sections = get_manual_document(lang)

    blocks: list[ManualBlock] = []
    order: list[str] = []

    def blank() -> None:
        blocks.append(ManualBlock(kind="blank"))

    def line(text: str) -> None:
        blocks.append(ManualBlock(kind="line", text=text))

    def toc_title(text: str) -> None:
        blocks.append(ManualBlock(kind="toc_title", text=text))

    def toc_item(text: str, section_id: str) -> None:
        blocks.append(ManualBlock(kind="toc_item", text=text, section_id=section_id))

    def section_title(text: str, section_id: str) -> None:
        blocks.append(ManualBlock(kind="section_title", text=text, section_id=section_id))

    def detail_title(text: str) -> None:
        blocks.append(ManualBlock(kind="detail_title", text=text))

    def paragraph(text: str) -> None:
        blocks.append(ManualBlock(kind="paragraph", text=text))

    def bullet(text: str) -> None:
        blocks.append(ManualBlock(kind="bullet", text=text))

    def divider() -> None:
        blocks.append(ManualBlock(kind="divider", text="-" * 60))

    line(get_manual_title(lang))
    line("=" * len(get_manual_title(lang)))
    blank()

    if lang == "pt_BR":
        paragraph(
            "Este manual descreve como operar o aplicativo Lúmen (modo de uso), cobrindo funcionalidades, atalhos, "
            "fluxo de trabalho sugerido, solução de problemas e informações sobre persistência de dados."
        )
        paragraph("Não é um guia de desenvolvimento.")
        blank()
        toc_title("Indice")

    else:
        paragraph(
            "This manual describes how to operate the Lúmen application (user guide), covering features, shortcuts, "
            "suggested workflows, troubleshooting, and information about data persistence."
        )
        paragraph("It is not a development guide.")
        blank()
        toc_title("Table of Contents")

    for idx, s in enumerate(sections, start=1):
        toc_item(f"{idx}. {s.title}", section_id=s.id)

    blank()
    divider()
    blank()

    for s in sections:
        order.append(s.id)

        section_title(s.title, section_id=s.id)
        blank()

        for p in s.paragraphs:
            paragraph(p)
            blank()

        for b in s.bullets:
            bullet(b)

        if s.bullets:
            blank()

        for d in s.details:
            detail_title(d.summary)
            blank()

            for p in d.paragraphs:
                paragraph(p)
                blank()

            for b in d.bullets:
                bullet(b)

            if d.bullets:
                blank()

        divider()
        blank()

    return tuple(blocks), tuple(order)


def get_manual_text(lang: str | None = None) -> str:
    text, _positions, _order = get_manual_text_with_positions(lang)
    return text


def get_manual_text_with_positions(lang: str | None = None,) -> tuple[str, Dict[str, int], Tuple[str, ...]]:
    lang = normalize_language(lang)
    sections = get_manual_document(lang)

    lines: list[str] = []
    positions: dict[str, int] = {}
    order: list[str] = []

    def add_line(s: str = "") -> None:
        lines.append(s)

    def current_offset() -> int:
        return sum(len(l) + 1 for l in lines)

    title = get_manual_title(lang)
    add_line(title)
    add_line("=" * len(title))
    add_line()

    if lang == "pt_BR":
        add_line(
            "Este manual descreve como operar o aplicativo Lúmen (modo de uso), cobrindo funcionalidades, atalhos, "
            "fluxo de trabalho sugerido, solução de problemas e informações sobre persistência de dados."
        )
        add_line("Não é um guia de desenvolvimento.")
        add_line()
        add_line("Indice")
        add_line("----------")

    else:
        add_line(
            "This manual describes how to operate the Lúmen application (user guide), covering features, shortcuts, "
            "suggested workflows, troubleshooting, and information about data persistence."
        )
        add_line("It is not a development guide.")
        add_line()
        add_line("Table of Contents")
        add_line("------------------------------")

    for idx, s in enumerate(sections, start=1):
        add_line(f"{idx}. {s.title}")

    add_line()
    add_line("-" * 60)
    add_line()

    for s in sections:
        positions[s.id] = current_offset()
        order.append(s.id)

        add_line(s.title)
        add_line("-" * len(s.title))
        add_line()

        for p in s.paragraphs:
            add_line(p)
            add_line()

        for b in s.bullets:
            add_line(f"- {b}")

        if s.bullets:
            add_line()

        for d in s.details:
            add_line(d.summary)
            add_line("." * len(d.summary))
            add_line()

            for p in d.paragraphs:
                add_line(p)
                add_line()

            for b in d.bullets:
                add_line(f"- {b}")

            if d.bullets:
                add_line()

        add_line("-" * 60)
        add_line()

    return "\n".join(lines), positions, tuple(order)

# ----------------------------
# Conteúdo do manual (texto)
# ----------------------------

_DOC_PT_BR: tuple[ManualSection, ...] = (
    ManualSection(
        id="visao-geral",
        title="Visão Geral",
        paragraphs=(
            "Lúmen é uma suíte de ferramentas para estudo composta por módulos principais: Leitor Acessível, Gestão de Tempo "
            "(Pomodoro e gerenciador de tarefas), Mapas Mentais, Método Feynman e Matriz de Eisenhower. "
            "A interface é organizada em abas; cada aba contém controles e ferramentas específicas ao módulo.",
        ),
    ),
    ManualSection(
        id="requisitos-basicos-usuario",
        title="Requisitos básicos (usuário)",
        bullets=(
            "Windows (testado).",
            "Conexão à Internet para Edge TTS (opcional).",
        ),
    ),
    ManualSection(
        id="como-iniciar-o-aplicativo",
        title="Como iniciar o aplicativo",
        bullets=(
            "Abra a aplicação e selecione a aba do módulo que deseja usar.",
            "No Leitor: carregue um documento ou cole um texto na área de leitura, ajuste fonte e zoom.",
            "Para ouvir: use o botão Ler para iniciar TTS; use Pausar ou Parar conforme necessário.",
            "Em Gestão de Tempo: crie tarefas, inicie Pomodoro para foco e registre progressos.",
            "Em Mapas Mentais e Feynman: crie, edite e salve seus projetos.",
            "Em Eisenhower: categorize tarefas e reorganize por prioridade.",
        ),
    ),
    ManualSection(
        id="abertura-e-controles-globais",
        title="Abertura e controles globais",
        paragraphs=(
            "Ao abrir o Lúmen você verá a janela principal com abas e uma barra de menus (Arquivo, Configurações, Idiomas, Vozes, Sobre). "
            "A barra de status exibe informações contextuais.",
        ),
    ),
    ManualSection(
        id="modulos",
        title="Módulos (detalhados por aba)",
        details=(
            ManualDetails(
                summary="Leitor Acessível — Aba 1",
                paragraphs=(
                    "Conteúdo: carregamento de PDFs, extração de texto, TTS (Edge ou local), controle de velocidade e volume, régua de foco e formatações de texto.",
                ),
                bullets=(
                    "Carregar PDF: Arquivo → Abrir (ou Ctrl+O).",
                    "▶️ Iniciar e Ler: inicia a leitura por TTS; o texto pode ser destacado conforme a leitura avança.",
                    "⏸️ Pausar e Continuar: pausa a leitura temporariamente e retoma depois.",
                    "⏹️ Parar: interrompe a leitura e esvazia a fila de áudio.",
                    "Régua de Foco: ativar/desativar pela barra; ESC fecha a régua.",
                    "Vozes: selecione o mecanismo (Edge TTS ou local) e a voz em Vozes → Selecionar voz.",
                ),
            ),
            ManualDetails(
                summary="Gestão de Tempo — Aba 2",
                paragraphs=(
                    "Conteúdo: temporizador Pomodoro configurável, tarefas estilo Kanban, registro de pomodoros e integração entre timer e tarefas.",
                ),
                bullets=(
                    "Crie e selecione uma tarefa, mova para Doing quando for estudar.",
                    "Inicie o Pomodoro com a tarefa selecionada para registrar progresso.",
                    "Use Pausar e Retomar para interrupções.",
                    "Consulte histórico para acompanhar produtividade.",
                ),
            ),
            ManualDetails(
                summary="Mapas Mentais — Aba 3",
                paragraphs=(
                    "Editor visual de nós e ligações, edição por duplo clique, exportação para imagem e salvamento de projeto.",
                ),
                bullets=(
                    "Novo mapa cria um canvas vazio.",
                    "Adicionar nó para inserir ideias; Conectar para ligar nós.",
                    "Arraste para reorganizar; exporte para PNG quando precisar.",
                ),
            ),
            ManualDetails(
                summary="Método Feynman — Aba 4",
                paragraphs=(
                    "Ferramenta para explicar conceitos em etapas: explicação simples, lacunas, revisão e avaliação de domínio.",
                ),
                bullets=(
                    "Crie um conceito e escreva uma explicação como para um leigo.",
                    "Registre pontos de dúvida e termos desconhecidos.",
                    "Revise e reescreva após pesquisar; salve e marque nível de domínio.",
                ),
            ),
            ManualDetails(
                summary="Matriz de Eisenhower — Aba 5",
                paragraphs=(
                    "Quadro de priorização com quatro quadrantes; suporte a data e hora, calendário e exportação simples quando disponível.",
                ),
                bullets=(
                    "Adicione tarefas e posicione por urgência e importância.",
                    "Arraste entre quadrantes conforme prioridades mudam.",
                    "Use o painel de calendário para tarefas agendadas.",
                ),
            ),
        ),
    ),
    ManualSection(
        id="menus-e-acoes-rapidas",
        title="Menus e ações rápidas",
        bullets=(
            "Arquivo: carregar e salvar projetos, exportar mapas, importar tarefas (quando disponível).",
            "Configurações: idioma, vozes e fonte padrão.",
            "Idiomas: muda idioma da interface e das strings.",
            "Ajuda: versão e documentação rápida.",
        ),
    ),
    ManualSection(
        id="sugestoes-de-uso-combinadas",
        title="Sugestões de uso combinadas",
        bullets=(
            "Leitura e Pomodoro: abra material no Leitor, ative régua de foco, vincule uma tarefa e inicie a sessão.",
            "Mapas e Feynman: transforme nós em explicações e revise depois.",
            "Eisenhower: priorize semanalmente e planeje pomodoros para o que importa.",
        ),
    ),
    ManualSection(
        id="solucao-de-problemas",
        title="Solução de problemas",
        details=(
            ManualDetails(
                summary="Sem som",
                bullets=(
                    "Verifique volume do sistema e do aplicativo.",
                    "Se estiver usando Edge TTS, confirme a conexão com a Internet.",
                ),
            ),
            ManualDetails(
                summary="PDF sem texto",
                bullets=(
                    "O PDF pode ser baseado em imagem; será necessário OCR.",
                    "Se aplicável, verifique bibliotecas como pdfplumber e pypdf.",
                ),
            ),
            ManualDetails(
                summary="Vozes não listadas",
                bullets=("Recarregue vozes ou reinicie o aplicativo.",),
            ),
            ManualDetails(
                summary="Erro ao salvar ou ler",
                bullets=(
                    "Verifique permissões da pasta de dados.",
                    "Consulte os logs para detalhes.",
                ),
            ),
        ),
    ),
    ManualSection(
        id="logs-e-diagnostico",
        title="Logs e diagnóstico",
        bullets=("O LogManager gera logs; verifique a pasta AppData\\Local\\Lumen\\logs (no Windows).",),
    ),
    ManualSection(
        id="armazenamento",
        title="Armazenamento e arquivos persistentes (resumo)",
        bullets=(
            "Tarefas: JSON (por exemplo, tarefas.json).",
            "Mapas: projeto (por exemplo, .map ou .json).",
            "Conceitos Feynman: conceitos.json.",
            "Configurações: config.json.",
            "Local sugerido: AppData\\Local\\Lumen (no Windows).",
        ),
    ),
    ManualSection(
        id="boas-praticas",
        title="Boas práticas de uso",
        bullets=(
            "Salve mapas e conceitos regularmente.",
            "Faça backups periódicos.",
            "Mantenha o aplicativo e dependências atualizados.",
        ),
    ),
    ManualSection(
        id="atalhos",
        title="Resumo rápido de atalhos",
        bullets=(
            "Ctrl+1 — 📖 Leitor Acessível  ",
            "Ctrl+2 — ⏱️ Gestão de Tempo",
            "Ctrl+3 — 🧠 Mapas Mentais",
            "Ctrl+4 — 🎓 Método Feynman",
            "Ctrl+5 — 🗂️ Matriz Eisenhower",
            "Ctrl+O — 📂 Carregar PDF",
            "Ctrl+R — ▶️ Ler",
            "Ctrl+P — ⏸️ Pausar",
            "Ctrl+T — ➕ Adicionar",
            "Ctrl+N — ➕ Adicionar Conceito",
            "Ctrl+S — 💾 Salvar",
            "Ctrl+L — 📂 Carregar",
            "Ctrl+Shift+F — 🔤 Fonte",
            "Ctrl+Shift+S — 🔔 Som",
            "Ctrl+Q — ❌ Sair",
            "F1 — ❓ Ajuda",
        ),
    ),
    ManualSection(
        id="faq",
        title="Perguntas frequentes (FAQ)",
        details=(
            ManualDetails(
                summary="Como deixar a voz mais natural?",
                paragraphs=("Use Edge TTS (vozes neurais) e ajuste velocidade e volume.",),
            ),
            ManualDetails(
                summary="Onde meus dados são salvos?",
                paragraphs=("No diretório de dados do app (Windows: AppData\\Local\\Lumen).",),
            ),
        ),
    ),
    ManualSection(
        id="suporte",
        title="Como obter ajuda e suporte",
        bullets=(
            "Use o menu Ajuda para versão e documentação.",
            "Para problemas técnicos, anexe logs ao abrir um issue. Contato: linceu_lighthouse@outlook.com.",
        ),
    ),
)

_DOC_EN_US: tuple[ManualSection, ...] = (
    ManualSection(
        id="overview",
        title="Overview",
        paragraphs=(
            "Lúmen is a study tool suite composed of core modules: Accessible Reader, Time Management (Pomodoro and task manager), "
            "Mind Maps, Feynman Method, and Eisenhower Matrix. The interface is organized into tabs; each tab contains controls "
            "and tools specific to its module.",
        ),
    ),
    ManualSection(
        id="basic-requirements-user",
        title="Basic Requirements (User)",
        bullets=(
            "Windows (tested).",
            "Internet connection for Edge TTS (optional).",
        ),
    ),
    ManualSection(
        id="how-to-start-the-application",
        title="How to Start the Application",
        bullets=(
            "Open the application and select the tab of the module you want to use.",
            "In the Reader: load a document or paste text into the reading area; adjust font and zoom.",
            "To listen: use the Read button to start TTS; use Pause or Stop as needed.",
            "In Time Management: create tasks, start Pomodoro for focus, and log progress.",
            "In Mind Maps and Feynman: create, edit, and save your projects.",
            "In Eisenhower: categorize tasks and reorganize by priority.",
        ),
    ),
    ManualSection(
        id="startup-and-global-controls",
        title="Startup and Global Controls",
        paragraphs=(
            "When opening Lúmen, you will see the main window with tabs and a menu bar (File, Settings, Languages, Voices, About). "
            "The status bar displays contextual information.",
        ),
    ),
    ManualSection(
        id="modules",
        title="Modules (Detailed by Tab)",
        details=(
            ManualDetails(
                summary="Accessible Reader — Tab 1",
                paragraphs=(
                    "Content: PDF loading, text extraction, TTS (Edge or local), speed and volume control, focus ruler, and text formatting.",
                ),
                bullets=(
                    "Load PDF: File → Open (or Ctrl+O).",
                    "▶️ Play and Read: starts TTS; text may be highlighted as reading progresses.",
                    "⏸️ Pause and Resume: temporarily pauses and continues later.",
                    "⏹️ Stop: stops reading and clears the audio queue.",
                    "Focus Ruler: toggle on the toolbar; ESC closes the ruler.",
                    "Voices: choose engine (Edge TTS or local) and select a voice in Voices → Select voice.",
                ),
            ),
            ManualDetails(
                summary="Time Management — Tab 2",
                paragraphs=(
                    "Content: configurable Pomodoro timer, Kanban-style tasks, Pomodoro logging, and integration between timer and tasks.",
                ),
                bullets=(
                    "Create and select a task, move it to Doing when you plan to work on it.",
                    "Start Pomodoro with a selected task to log progress.",
                    "Use Pause and Resume for interruptions.",
                    "Review history to track productivity.",
                ),
            ),
            ManualDetails(
                summary="Mind Maps — Tab 3",
                paragraphs=("Visual editor for nodes and links, double-click editing, image export, and project saving.",),
                bullets=(
                    "New map creates an empty canvas.",
                    "Add nodes to capture ideas; Connect to link nodes.",
                    "Drag to reorganize; export to PNG when needed.",
                ),
            ),
            ManualDetails(
                summary="Feynman Method — Tab 4",
                paragraphs=("Tool to explain concepts in steps: simple explanation, gaps, review, and mastery assessment.",),
                bullets=(
                    "Create a concept and write an explanation as if to a layperson.",
                    "Record doubts and unknown terms.",
                    "Review and rewrite after research; save and mark mastery level.",
                ),
            ),
            ManualDetails(
                summary="Eisenhower Matrix — Tab 5",
                paragraphs=("Prioritization board with four quadrants; supports date and time, calendar, and simple export when available.",),
                bullets=(
                    "Add tasks and position them by urgency and importance.",
                    "Drag tasks between quadrants as priorities change.",
                    "Use the calendar panel for scheduled tasks.",
                ),
            ),
        ),
    ),
    ManualSection(
        id="menus-and-quick-actions",
        title="Menus and Quick Actions",
        bullets=(
            "File: load and save projects, export maps, import tasks (when available).",
            "Settings: language, voices, and default font.",
            "Languages: changes UI language and strings.",
            "Help: version and quick documentation.",
        ),
    ),
    ManualSection(
        id="combined-usage-suggestions",
        title="Combined Usage Suggestions",
        bullets=(
            "Reading and Pomodoro: open material in the Reader, enable focus ruler, link a task, and start a session.",
            "Mind Maps and Feynman: turn nodes into explanations and review later.",
            "Eisenhower: prioritize weekly and plan Pomodoros for what matters.",
        ),
    ),
    ManualSection(
        id="troubleshooting",
        title="Troubleshooting",
        details=(
            ManualDetails(
                summary="No sound",
                bullets=(
                    "Check system and application volume.",
                    "If using Edge TTS, confirm Internet connectivity.",
                ),
            ),
            ManualDetails(
                summary="PDF without text",
                bullets=(
                    "The PDF may be image-based; OCR may be required.",
                    "If applicable, check libraries such as pdfplumber and pypdf.",
                ),
            ),
            ManualDetails(
                summary="Voices not listed",
                bullets=("Reload voices or restart the app.",),
            ),
            ManualDetails(
                summary="Error saving or reading",
                bullets=(
                    "Check data folder permissions.",
                    "See logs for details.",
                ),
            ),
        ),
    ),
    ManualSection(
        id="logs-and-diagnostics",
        title="Logs and Diagnostics",
        bullets=("LogManager generates logs; check the app data folder at AppData\\Local\\Lumen\\logs (on Windows).",),
    ),
    ManualSection(
        id="storage",
        title="Storage / Persistent Files (Summary)",
        bullets=(
            "Tasks: JSON (for example, tasks.json).",
            "Maps: project files (for example, .map or .json).",
            "Feynman concepts: concepts.json.",
            "Settings: config.json.",
            "Suggested location: AppData\\Local\\Lumen (on Windows).",
        ),
    ),
    ManualSection(
        id="best-practices",
        title="Best Practices",
        bullets=(
            "Save maps and concepts regularly.",
            "Perform periodic backups.",
            "Keep the app and dependencies up to date.",
        ),
    ),
    ManualSection(
        id="shortcuts",
        title="Quick Shortcut Summary",
        bullets=(
            "Ctrl+1 — 📖 Accessible Reader ",
            "Ctrl+2 — ⏱️ Time Management ",
            "Ctrl+3 — 🧠 Mind Maps",
            "Ctrl+4 — 🎓 Feynman Method",
            "Ctrl+5 — 🗂️ Eisenhower Matrix",
            "Ctrl+O — 📂 Load PDF",
            "Ctrl+R — ▶️ Read",
            "Ctrl+P — ⏸️ Pause",
            "Ctrl+T — ➕ Add",
            "Ctrl+N — ➕ Add Concept",
            "Ctrl+S — 💾 Save",
            "Ctrl+L — 📂 Load",
            "Ctrl+Shift+F — 🔤 Font...",
            "Ctrl+Shift+S — 🔔 Sound...",
            "Ctrl+Q — ❌ Exit",
            "F1 — ❓ Help",
        ),
    ),
    ManualSection(
        id="faq",
        title="FAQ (Frequently Asked Questions)",
        details=(
            ManualDetails(
                summary="How do I make the voice more natural?",
                paragraphs=("Use Edge TTS (neural voices) and adjust speed and volume.",),
            ),
            ManualDetails(
                summary="Where are my data saved?",
                paragraphs=("In the app data directory (Windows: AppData\\Local\\Lumen).",),
            ),
        ),
    ),
    ManualSection(
        id="support",
        title="How to Get Help / Support",
        bullets=(
            "Use the Help menu for version and documentation.",
            "For technical issues, attach logs when opening an issue. Contact: linceu_lighthouse@outlook.com.",
        ),
    ),
)
