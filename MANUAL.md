# Manual de Utilização — Lúmen / User Manual — Lúmen

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
- [Módulos](#módulos-detalhados-por-aba)
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
- [Boas práticas de uso](#boas-práticas-de-uso)
- [Resumo rápido de atalhos](#resumo-rápido-de-atalhos)
- [FAQ](#perguntas-frequentes-faq)
- [Como obter ajuda / suporte](#como-obter-ajuda--suporte)

---

## <a id="visão-geral"></a>Visão Geral
Lúmen é uma suíte de ferramentas para estudo composta por módulos principais: Leitor Acessível, Gestão de Tempo (Pomodoro + Gerenciador de Tarefas), Mapas Mentais, Método Feynman e Matriz de Eisenhower. A interface é organizada em abas; cada aba contém controles e ferramentas específicas ao módulo.

## <a id="requisitos-básicos-usuário"></a>Requisitos básicos (usuário)
- Windows (testado).
- Conexão à Internet para Edge TTS (opcional).

## <a id="como-iniciar-o-aplicativo"></a>Como iniciar o aplicativo
1. Abra a aplicação e selecione a aba do módulo que deseja usar.  
2. No Leitor: carregue um documento ou cole/cole o texto na área de leitura, ajuste fonte e zoom.  
3. Para ouvir: use o botão "Ler" para iniciar TTS; use Pausar/Parar conforme necessário.  
4. Em Gestão de Tempo: crie tarefas, inicie Pomodoro para foco e registre progressos.  
5. Em Mapas Mentais e Feynman: crie, edite e salve seus projetos.  
6. Em Eisenhower: categorize tarefas e reorganize por prioridade.

## <a id="abertura-e-controles-globais"></a>Abertura e controles globais
Ao abrir o Lúmen verá a janela principal com abas e uma barra de menus (Arquivo, Configurações, Idiomas, Vozes, Sobre). A barra de status exibe informações contextuais.

---

## <a id="módulos-detalhados-por-aba"></a>Módulos (detalhados por aba)

### <a id="leitor-acessível---aba-1"></a>Leitor Acessível — Aba 1

<details>
<summary>Resumo rápido — Leitor Acessível (clique para expandir/recolher)</summary>

Conteúdo: carregamento de PDFs, extração de texto, TTS (Edge ou local), controle de velocidade/volume, régua de foco e formatações de texto.

</details>

<details>
<summary>Descrição completa — Leitor Acessível</summary>

Principais ações
- Carregar PDF: <span style="font-size:1.1em;"><code>Arquivo → Abrir</code></span> (ou <span style="font-size:1.1em;"><code>Ctrl+O</code></span>). O texto extraído aparece na área de leitura; se o PDF não contiver texto.
- Play / ▶️ Ler: inicia a leitura por TTS; o texto é destacado conforme a leitura avança.
- Pausar / ⏸️ e Continuar: pausa a leitura temporariamente.
- Stop / ⏹️: interrompe a leitura e esvazia a fila de áudio.

Controles e opções (detalhado)
- Velocidade (slider): ajusta a velocidade do TTS. Valores menores tornam a leitura mais lenta e compreensível.
- Volume (slider): controla o volume do player interno.
- Fonte (combo): escolha família e tamanho da fonte para melhor legibilidade.
- Botões de edição: <span style="font-size:1.1em;"><code>Novo</code></span> limpa o texto; <span style="font-size:1.1em;"><code>Salvar Como</code></span> exporta em <span style="font-size:1.1em;"><code>.txt</code></span>.

PDF — barra de ferramentas
- Navegação por página: <span style="font-size:1.1em;"><code>Primeira</code></span>, <span style="font-size:1.1em;"><code>Anterior</code></span>, <span style="font-size:1.1em;"><code>Próxima</code></span>, <span style="font-size:1.1em;"><code>Última</code></span> e entrada numérica para ir direto à página.
- Zoom: selecione 50%, 100%, <span style="font-size:1.1em;"><code>Ajustar à largura</code></span> ou <span style="font-size:1.1em;"><code>Ajustar à página</code></span>.
- Modos: página única ou rolagem contínua.
- Hand Mode: mantenha pressionado e arraste para mover a página.

Régua de Foco
- Ativar/Desativar: botão na barra de ferramentas.
- Mover/Redimensionar: arraste com o mouse; use as setas do teclado para ajustes finos; pressione <span style="font-size:1.1em;"><code>ESC</code></span> para fechar a régua.
- Sincronização: o estado da régua é refletido no menu principal (<span style="font-size:1.1em;"><code>Regua de Foco</code></span>).

Vozes e TTS
- Mecanismos: <span style="font-size:1.1em;"><code>Edge TTS</code></span> (neural, requer Internet) ou motores locais.
- Seleção de voz: <span style="font-size:1.1em;"><code>Vozes → Selecionar voz</code></span>. A escolha pode ser gravada nas configurações do aplicativo.

Como usar — passo a passo
1) Abra um PDF (<span style="font-size:1.1em;"><code>Ctrl+O</code></span>).  
2) Ajuste visual (zoom/fonte) para leitura confortável.  
3) Ative a régua de foco se preferir leitura linha-a-linha.  
4) Clique em <span style="font-size:1.1em;"><code>Play</code></span> (<span style="font-size:1.1em;"><code>Ctrl+R</code></span>) para iniciar a leitura; use <span style="font-size:1.1em;"><code>Pausar</code></span>/<span style="font-size:1.1em;"><code>Stop</code></span> conforme necessário.  
5) Salve o texto extraído via <span style="font-size:1.1em;"><code>Salvar Como</code></span> se precisar editar ou arquivar.

Dicas práticas
- Se não houver som, verifique volume do sistema e do aplicativo.  
- Para voz mais natural, use <span style="font-size:1.1em;"><code>Edge TTS</code></span> quando tiver conexão.  
- Em PDFs escaneados.

</details>

---

### <a id="gestão-de-tempo---aba-2"></a>Gestão de Tempo — Aba 2

<details>
<summary>Resumo rápido — Gestão de Tempo (Pomodoro + Kanban)</summary>

Conteúdo: temporizador Pomodoro configurável, gerenciador de tarefas estilo Kanban, registro de pomodoros e integração entre timer e tarefas.

</details>

<details>
<summary>Descrição completa — Gestão de Tempo</summary>

Pomodoro (passo a passo)
1) Criar/selecionar tarefa: adicione tarefa no Kanban e mova-a para <span style="font-size:1.1em;"><code>Doing</code></span> quando for estudá-la.  
2) Iniciar Pomodoro: com a tarefa selecionada, clique em <span style="font-size:1.1em;"><code>Iniciar</code></span>. O temporizador contará o período de foco.
3) Pausar/Retomar: use <span style="font-size:1.1em;"><code>Pausar</code></span> para interrupções; <span style="font-size:1.1em;"><code>Retomar</code></span> continua a contagem.  
4) Fim do ciclo: o app tocará um som; marque o pomodoro como realizado ou adicione nota à tarefa.

Controles e opções
- Ajuste de tempos: configure duração do foco e dos descansos nas configurações do módulo.
- Vínculo de tarefa: selecionar uma tarefa antes de iniciar o temporizador registra o pomodoro para ela.
- Histórico: consulte registro de pomodoros para acompanhar produtividade.

Gerenciador de Tarefas (Kanban)
- Adicionar tarefa: clique em <span style="font-size:1.1em;"><code>Adicionar</code></span> (ou <span style="font-size:1.1em;"><code>Ctrl+T</code></span>) e preencha título, prioridade e estimativa de pomodoros.
- Mover tarefas: arraste entre <span style="font-size:1.1em;"><code>Todo</code></span>, <span style="font-size:1.1em;"><code>Doing</code></span> e <span style="font-size:1.1em;"><code>Done</code></span>.
- Editar/Remover: use o menu de contexto (clique direito) para editar detalhes ou excluir.

Dicas práticas
- Foque em uma tarefa por vez no <span style="font-size:1.1em;"><code>Doing</code></span> para manter disciplina.  
- Use estimativas de pomodoro para planejar sessões de estudo ao longo do dia.

</details>

---

### <a id="mapas-mentais---aba-3"></a>Mapas Mentais — Aba 3

<details>
<summary>Resumo rápido — Mapas Mentais</summary>

Editor visual de nós e ligações, edição por duplo clique, exportação para imagem e salvamento de projeto.

</details>

<details>
<summary>Descrição completa — Mapas Mentais</summary>

Criar e editar mapas (passo a passo)
1) Novo mapa: <span style="font-size:1.1em;"><code>Arquivo → Novo</code></span> cria um canvas vazio.  
2) Adicionar nó: clique em <span style="font-size:1.1em;"><code>Adicionar Nó</code></span> ou botão <span style="font-size:1.1em;"><code>+</code></span> e digite o texto.  
3) Conectar nós: ative <span style="font-size:1.1em;"><code>Conectar</code></span> e clique na origem e no destino.  
4) Editar nó: dê duplo clique para alterar texto, cor ou adicionar nota.  
5) Reorganizar: arraste nós livremente para ajustar a estrutura.

Controles e opções
- Propriedades do nó: defina cor, tamanho e notas para cada nó.  
- Exportar: <span style="font-size:1.1em;"><code>Exportar → PNG</code></span> gera imagem pronta para impressão ou apresentação.

Dicas práticas
- Comece pelo nó central com o tema principal; crie ramos para subtemas.  
- Use cores e ícones para categorizar informações e facilitar memorização.

</details>

---

### <a id="método-feynman---aba-4"></a>Método Feynman — Aba 4

<details>
<summary>Resumo rápido — Método Feynman</summary>

Ferramenta para explicar conceitos com etapas: explicação simples, lacunas, revisão e avaliação de domínio.

</details>

<details>
<summary>Descrição completa — Método Feynman</summary>

Fluxo básico (passo a passo)
1) Criar conceito: clique em <span style="font-size:1.1em;"><code>Novo</code></span> (<span style="font-size:1.1em;"><code>Ctrl+N</code></span>), informe o título.  
2) Escrever explicação simples: explique o conceito como para um leigo.  
3) Identificar lacunas: registre dúvidas e termos desconhecidos no campo <span style="font-size:1.1em;"><code>Pontos de Dúvida</code></span>.  
4) Revisar e reescrever: pesquise, preencha lacunas e reescreva a explicação.  
5) Salvar e avaliar: salve o conceito e marque o nível de domínio.

Controles e opções
- Campos: <span style="font-size:1.1em;"><code>Título</code></span>, <span style="font-size:1.1em;"><code>Explicação</code></span>, <span style="font-size:1.1em;"><code>Lacunas</code></span>, <span style="font-size:1.1em;"><code>Resumo Revisado</code></span>, <span style="font-size:1.1em;"><code>Nível de Domínio</code></span>.
- Lista: use a lista à esquerda para selecionar e editar conceitos existentes.

Dicas práticas
- Escreva de forma simples e curta; evite termos técnicos sem explicação.  
- Revise periodicamente: conceitos revisados ajudam a consolidar memorização.

</details>

---

### <a id="matriz-de-eisenhower---aba-5"></a>Matriz de Eisenhower — Aba 5

<details>
<summary>Resumo rápido — Matriz de Eisenhower</summary>

Quadro de priorização com quatro quadrantes; suporte a data/hora, calendário e exportação simples.

</details>

<details>
<summary>Descrição completa — Matriz de Eisenhower</summary>

Como usar (passo a passo)
1) Adicionar tarefa: clique em <span style="font-size:1.1em;"><code>Adicionar</code></span>, informe título e, se desejar, data/hora.  
2) Escolher quadrante: defina prioridade/urgência para posicionar a tarefa.  
3) Reorganizar: arraste tarefas entre quadrantes conforme prioridades mudam.  
4) Calendário: abra o painel <span style="font-size:1.1em;"><code>Calendário</code></span> para visualizar tarefas agendadas.

Controles e opções
- Quadrantes: arraste para mover; menu de contexto para editar ou excluir.  
- Exportar: quando disponível, use <span style="font-size:1.1em;"><code>Exportar</code></span> para CSV/Excel.

Dicas práticas
- Reserve tempo semanal para revisar e redistribuir tarefas.  
- Use os quadrantes para decidir onde alocar pomodoros e esforços de estudo.

</details>

---

---

## <a id="menus-e-ações-rápidas"></a>Menus e ações rápidas
- Arquivo: comandos para carregar/salvar projetos, exportar mapas, importar tarefas.
- Configurações: Idioma, Vozes, Fonte padrão.
- Idiomas: mudar idioma da interface e das strings de módulos.
- Ajuda: versão e documentação rápida.

## <a id="sugestões-de-uso-combinadas"></a>Sugestões de uso combinadas
- Leitura + Pomodoro: abra material no Leitor, ative régua de foco, vincule tarefa ao Pomodoro e inicie sessão.
- Mapas + Feynman: crie nós e registre explicações no Feynman para revisão.
- Eisenhower para priorizar semanalmente e planejar pomodoros.

## <a id="solução-de-problemas-troubleshooting"></a>Solução de problemas (Troubleshooting)
- Sem som:
  - Verificar volume do sistema e do app.
  - Edge TTS: confirmar Internet.
- PDF sem texto:
  - PDF pode ser imagem (use OCR).
  - Verificar bibliotecas: pdfplumber, pypdf.
- Vozes não listadas:
  - Recarregar vozes ou reiniciar app.
- Erro ao salvar/ler:
  - Verificar permissões de pasta; localizar arquivos no diretório de dados.

## <a id="logs-e-diagnóstico"></a>Logs e diagnóstico
- LogManager gera logs; verificar pasta de dados <span style="font-size:1.1em;"><code>C:\Users\...\AppData\Local\Lumen\logs</code></span>.

## <a id="armazenamento--arquivos-persistentes-resumo"></a>Armazenamento / Arquivos persistentes (resumo)
- Tarefas: JSON (ex.: tarefas.json).  
- Mapas: projeto (.map, .json).  
- Conceitos Feynman: conceitos.json.  
- Configurações: config.json.  
- Local sugerido: <span style="font-size:1.1em;"><code>%APPDATA%\Local\Lumen</code></span>.

## <a id="boas-práticas-de-uso"></a>Boas práticas de uso
- Salve mapas e conceitos regularmente.
- Faça backups periódicos.
- Mantenha app e dependências atualizados.

## <a id="resumo-rápido-de-atalhos"></a>Resumo rápido de atalhos
- Ctrl+1 — 📖 Leitor Acessível  
- Ctrl+2 — ⏱️ Gestão de Tempo  
- Ctrl+3 — 🧠 Mapas Mentais  
- Ctrl+4 — 🎓 Método Feynman  
- Ctrl+5 — 🗂️ Matriz Eisenhower  
- Ctrl+O — 📁 Carregar PDF  
- Ctrl+R — ▶️ Ler  
- Ctrl+P — ⏸️ Pausar  
- Ctrl+T — ➕ Adicionar  
- Ctrl+N — ➕ Adicionar Conceito  
- Ctrl+S — 💾 Salvar  
- Ctrl+L — 📂 Carregar  
- Ctrl+Shift+F — 🔤 Fonte...  
- Ctrl+Shift+S — 🔔 Som...  
- Ctrl+Q — 🚪 Sair  
- F1 — Ajuda

## <a id="perguntas-frequentes-faq"></a>Perguntas Frequentes (FAQ)
- Como deixar voz mais natural? Use Edge TTS (vozes neurais) e ajuste velocidade/volume.
- Onde meus dados são salvos? No diretório de dados do app (<span style="font-size:1.1em;"><code>%APPDATA%</code></span> / <span style="font-size:1.1em;"><code>~/.local/Lumen</code></span>).

## <a id="como-obter-ajuda--suporte"></a>Como obter ajuda / suporte
- Menu Ajuda para versão/documentação.
- Para problemas técnicos, anexe logs ao abrir um issue, envie para <span style="font-size:1.1em;"><code>linceu_lighthouse@outlook.com</code></span>.

</details>

---

## <a id="enus"></a>🇺🇸 English (US)

<details>
<summary>Click to expand the manual in English</summary>

# User Manual — Lúmen (EN‑US)

> This manual describes how to operate the Lúmen application (user guide), covering features, shortcuts, suggested workflows, troubleshooting, and information about data persistence. It is not a development guide.

## Table of Contents
- [Overview](#overview)
- [Basic Requirements (User)](#basic-requirements-user)
- [How to Start the Application](#how-to-start-the-application)
- [Startup and Global Controls](#startup-and-global-controls)
- [Modules](#modules-detailed-by-tab)
  - [Accessible Reader — Tab 1](#accessible-reader---tab-1)
  - [Time Management — Tab 2](#time-management---tab-2)
  - [Mind Maps — Tab 3](#mind-maps---tab-3)
  - [Feynman Method — Tab 4](#feynman-method---tab-4)
  - [Eisenhower Matrix — Tab 5](#eisenhower-matrix---tab-5)
- [Menus and Quick Actions](#menus-and-quick-actions)
- [Combined Usage Suggestions](#combined-usage-suggestions)
- [Troubleshooting](#troubleshooting)
- [Logs and Diagnostics](#logs-and-diagnostics)
- [Storage / Persistent Files (Summary)](#storage--persistent-files-summary)
- [Best Practices](#best-practices)
- [Quick Shortcut Summary](#quick-shortcut-summary)
- [FAQ](#frequently-asked-questions-faq)
- [How to Get Help / Support](#how-to-get-help--support)

---

## <a id="overview"></a> Overview
Lúmen is a study tool suite composed of core modules: Accessible Reader, Time Management (Pomodoro + Task Manager), Mind Maps, Feynman Method, and Eisenhower Matrix. The interface is organized into tabs; each tab contains controls and tools specific to its module.

## <a id="basic-requirements-user"></a>Basic Requirements (User)
- Windows (tested).
- Internet connection for Edge TTS (optional).

## <a id="how-to-start-the-application"></a>How to Start the Application
1. Open the application and select the tab of the module you want to use.  
2. In the Reader: load a document or paste text into the reading area; adjust font and zoom.  
3. To listen: use the **Read** button to start TTS; use **Pause/Stop** as needed.  
4. In Time Management: create tasks, start Pomodoro for focus, and log progress.  
5. In Mind Maps and Feynman: create, edit, and save your projects.  
6. In Eisenhower: categorize tasks and reorganize by priority.

## <a id="startup-and-global-controls"></a>Startup and Global Controls
When opening Lúmen, you will see the main window with tabs and a menu bar (**File**, **Settings**, **Languages**, **Voices**, **About**). The status bar displays contextual information.

---

## <a id="modules-detailed-by-tab"></a>Modules (Detailed by Tab)

### <a id="accessible-reader---tab-1"></a>Accessible Reader — Tab 1

<details>
<summary>Quick Summary — Accessible Reader (click to expand/collapse)</summary>

Content: PDF loading, text extraction, TTS (Edge or local), speed/volume control, focus ruler, and text formatting.

</details>

<details>
<summary>Full Description — Accessible Reader</summary>

Main actions
- Load PDF: <span style="font-size:1.1em;"><code>File → Open</code></span> (or <span style="font-size:1.1em;"><code>Ctrl+O</code></span>). Extracted text appears in the reading area; if the PDF does not contain text.
- Play / ▶️ Read: starts TTS; text is highlighted as reading progresses.
- Pause / ⏸️ and Resume: temporarily pauses reading.
- Stop / ⏹️: stops reading and clears the audio queue.

Controls and options (detailed)
- Speed (slider): adjusts TTS speed. Lower values make reading slower and more intelligible.
- Volume (slider): controls the internal player volume.
- Font (combo): choose font family and size for better readability.
- Editing buttons: <span style="font-size:1.1em;"><code>New</code></span> clears the text; <span style="font-size:1.1em;"><code>Save As</code></span> exports to <span style="font-size:1.1em;"><code>.txt</code></span>.

PDF — toolbar
- Page navigation: <span style="font-size:1.1em;"><code>First</code></span>, <span style="font-size:1.1em;"><code>Previous</code></span>, <span style="font-size:1.1em;"><code>Next</code></span>, <span style="font-size:1.1em;"><code>Last</code></span>, and numeric input to jump to a page.
- Zoom: select 50%, 100%, <span style="font-size:1.1em;"><code>Fit to Width</code></span>, or <span style="font-size:1.1em;"><code>Fit to Page</code></span>.
- Modes: single page or continuous scrolling.
- Hand Mode: press and drag to move the page.

Focus Ruler
- Enable/Disable: toolbar button.
- Move/Resize: drag with the mouse; use arrow keys for fine adjustments; press <span style="font-size:1.1em;"><code>ESC</code></span> to close the ruler.
- Synchronization: the ruler state is reflected in the main menu (**Focus Ruler**).

Voices and TTS
- Engines: <span style="font-size:1.1em;"><code>Edge TTS</code></span> (neural, requires Internet) or local engines.
- Voice selection: <span style="font-size:1.1em;"><code>Voices → Select Voice</code></span>. The choice can be saved in the application settings.

How to use — step by step
1) Open a PDF (<span style="font-size:1.1em;"><code>Ctrl+O</code></span>).  
2) Adjust visuals (zoom/font) for comfortable reading.  
3) Enable the focus ruler if you prefer line-by-line reading.  
4) Click <span style="font-size:1.1em;"><code>Play</code></span> (<span style="font-size:1.1em;"><code>Ctrl+R</code></span>) to start reading; use <span style="font-size:1.1em;"><code>Pause</code></span>/<span style="font-size:1.1em;"><code>Stop</code></span> as needed.  
5) Save extracted text via <span style="font-size:1.1em;"><code>Save As</code></span> if you need to edit or archive it.

Practical tips
- If there is no sound, check system and application volume.  
- For more natural voice, use <span style="font-size:1.1em;"><code>Edge TTS</code></span> when connected.  
- For scanned PDFs.

</details>

---

### <a id="time-management---tab-2"></a>Time Management — Tab 2

<details>
<summary>Quick Summary — Time Management (Pomodoro + Kanban)</summary>

Content: configurable Pomodoro timer, Kanban-style task manager, Pomodoro logging, and integration between timer and tasks.

</details>

<details>
<summary>Full Description — Time Management</summary>

Pomodoro (step by step)
1) Create/select task: add a task in the Kanban and move it to <span style="font-size:1.1em;"><code>Doing</code></span> when you plan to work on it.  
2) Start Pomodoro: with the task selected, click <span style="font-size:1.1em;"><code>Start</code></span>. The timer counts the focus period.
3) Pause/Resume: use <span style="font-size:1.1em;"><code>Pause</code></span> for interruptions; <span style="font-size:1.1em;"><code>Resume</code></span> continues the count.  
4) End of cycle: the app plays a sound; mark the Pomodoro as completed or add a note to the task.

Controls and options
- Time settings: configure focus and break durations in the module settings.
- Task linkage: selecting a task before starting the timer logs the Pomodoro to it.
- History: review Pomodoro logs to track productivity.

Task Manager (Kanban)
- Add task: click <span style="font-size:1.1em;"><code>Add</code></span> (or <span style="font-size:1.1em;"><code>Ctrl+T</code></span>) and fill in title, priority, and Pomodoro estimate.
- Move tasks: drag between <span style="font-size:1.1em;"><code>Todo</code></span>, <span style="font-size:1.1em;"><code>Doing</code></span>, and <span style="font-size:1.1em;"><code>Done</code></span>.
- Edit/Remove: use the context menu (right-click) to edit details or delete.

Practical tips
- Focus on one task at a time in <span style="font-size:1.1em;"><code>Doing</code></span> to maintain discipline.  
- Use Pomodoro estimates to plan study sessions throughout the day.

</details>

---

### <a id="mind-maps---tab-3"></a>Mind Maps — Tab 3

<details>
<summary>Quick Summary — Mind Maps</summary>

Visual editor for nodes and links, double-click editing, image export, and project saving.

</details>

<details>
<summary>Full Description — Mind Maps</summary>

Create and edit maps (step by step)
1) New map: <span style="font-size:1.1em;"><code>File → New</code></span> creates an empty canvas.  
2) Add node: click <span style="font-size:1.1em;"><code>Add Node</code></span> or the <span style="font-size:1.1em;"><code>+</code></span> button and enter text.  
3) Connect nodes: enable <span style="font-size:1.1em;"><code>Connect</code></span> and click source and destination.  
4) Edit node: double-click to change text, color, or add a note.  
5) Reorganize: drag nodes freely to adjust structure.

Controls and options
- Node properties: define color, size, and notes per node.  
- Export: <span style="font-size:1.1em;"><code>Export → PNG</code></span> generates an image ready for printing or presentation.

Practical tips
- Start with a central node for the main theme; create branches for subtopics.  
- Use colors and icons to categorize information and aid memorization.

</details>

---

### <a id="feynman-method---tab-4"></a>Feynman Method — Tab 4

<details>
<summary>Quick Summary — Feynman Method</summary>

Tool to explain concepts through steps: simple explanation, gaps, review, and mastery assessment.

</details>

<details>
<summary>Full Description — Feynman Method</summary>

Basic flow (step by step)
1) Create concept: click <span style="font-size:1.1em;"><code>New</code></span> (<span style="font-size:1.1em;"><code>Ctrl+N</code></span>), enter the title.  
2) Write a simple explanation: explain the concept as if to a layperson.  
3) Identify gaps: record questions and unknown terms in the <span style="font-size:1.1em;"><code>Points of Doubt</code></span> field.  
4) Review and rewrite: research, fill gaps, and rewrite the explanation.  
5) Save and assess: save the concept and mark the mastery level.

Controls and options
- Fields: <span style="font-size:1.1em;"><code>Title</code></span>, <span style="font-size:1.1em;"><code>Explanation</code></span>, <span style="font-size:1.1em;"><code>Gaps</code></span>, <span style="font-size:1.1em;"><code>Revised Summary</code></span>, <span style="font-size:1.1em;"><code>Mastery Level</code></span>.
- List: use the list on the left to select and edit existing concepts.

Practical tips
- Write simply and concisely; avoid technical terms without explanation.  
- Review periodically: revised concepts help consolidate memory.

</details>

---

### <a id="eisenhower-matrix---tab-5"></a>Eisenhower Matrix — Tab 5

<details>
<summary>Quick Summary — Eisenhower Matrix</summary>

Prioritization board with four quadrants; supports date/time, calendar, and simple export.

</details>

<details>
<summary>Full Description — Eisenhower Matrix</summary>

How to use (step by step)
1) Add task: click <span style="font-size:1.1em;"><code>Add</code></span>, enter title and optionally date/time.  
2) Choose quadrant: set priority/urgency to position the task.  
3) Reorganize: drag tasks between quadrants as priorities change.  
4) Calendar: open the <span style="font-size:1.1em;"><code>Calendar</code></span> panel to view scheduled tasks.

Controls and options
- Quadrants: drag to move; context menu to edit or delete.  
- Export: when available, use <span style="font-size:1.1em;"><code>Export</code></span> to CSV/Excel.

Practical tips
- Reserve weekly time to review and redistribute tasks.  
- Use quadrants to decide where to allocate Pomodoros and study effort.

</details>

---

---

## <a id="menus-and-quick-actions"></a>Menus and Quick Actions
- File: commands to load/save projects, export maps, import tasks.
- Settings: Language, Voices, Default Font.
- Languages: change interface language and module strings.
- Help: version and quick documentation.

## <a id="combined-usage-suggestions"></a>Combined Usage Suggestions
- Reading + Pomodoro: open material in the Reader, enable focus ruler, link a task to Pomodoro, and start a session.
- Mind Maps + Feynman: create nodes and record explanations in Feynman for review.
- Eisenhower to prioritize weekly and plan Pomodoros.

## <a id="troubleshooting"></a>Troubleshooting
- No sound:
  - Check system and app volume.
  - Edge TTS: confirm Internet connection.
- PDF without text:
  - The PDF may be image-based (use OCR).
  - Check libraries: pdfplumber, pypdf.
- Voices not listed:
  - Reload voices or restart the app.
- Error saving/reading:
  - Check folder permissions; locate files in the data directory.

## <a id="logs-and-diagnostics"></a>Logs and Diagnostics
- LogManager generates logs; check the data folder <span style="font-size:1.1em;"><code>C:\Users\...\AppData\Local\Lumen\logs</code></span>.

## <a id="storage--persistent-files-summary"></a>Storage / Persistent Files (Summary)
- Tasks: JSON (e.g., tasks.json).  
- Maps: project (.map, .json).  
- Feynman Concepts: concepts.json.  
- Settings: config.json.  
- Suggested location: <span style="font-size:1.1em;"><code>%APPDATA%\Local\Lumen</code></span>.

## <a id="best-practices"></a>Best Practices
- Save maps and concepts regularly.
- Perform periodic backups.
- Keep the app and dependencies up to date.

## <a id="quick-shortcut-summary"></a>Quick Shortcut Summary
- Ctrl+1 — 📖 Accessible Reader  
- Ctrl+2 — ⏱️ Time Management  
- Ctrl+3 — 🧠 Mind Maps  
- Ctrl+4 — 🎓 Feynman Method  
- Ctrl+5 — 🗂️ Eisenhower Matrix  
- Ctrl+O — 📁 Load PDF  
- Ctrl+R — ▶️ Read  
- Ctrl+P — ⏸️ Pause  
- Ctrl+T — ➕ Add  
- Ctrl+N — ➕ Add Concept  
- Ctrl+S — 💾 Save  
- Ctrl+L — 📂 Load  
- Ctrl+Shift+F — 🔤 Font...  
- Ctrl+Shift+S — 🔔 Sound...  
- Ctrl+Q — 🚪 Exit  
- F1 — Help

## <a id="frequently-asked-questions-faq"></a>Frequently Asked Questions (FAQ)
- How do I make the voice more natural? Use Edge TTS (neural voices) and adjust speed/volume.
- Where are my data saved? In the app data directory (<span style="font-size:1.1em;"><code>%APPDATA%</code></span> / <span style="font-size:1.1em;"><code>~/.local/Lumen</code></span>).

## <a id="how-to-get-help--support"></a>How to Get Help / Support
- Help menu for version/documentation.
- For technical issues, attach logs when opening an issue, or send them to <span style="font-size:1.1em;"><code>linceu_lighthouse@outlook.com</code></span>.

</details>

---

Arquivo atualizado: <span style="font-size:1.1em;"><code>MANUAL.md</code></span> com versões em Português e Inglês e blocos expansíveis por seção.  
File updated: <span style="font-size:1.1em;"><code>MANUAL.md</code></span> with Portuguese and English versions and expandable blocks per section.
