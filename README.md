<!-- Multilanguage README.md for Lúmen -->

<p align="center">
  <b>Selecione o idioma / Select language:</b><br>
  <a href="#ptbr">🇧🇷 Português (BR)</a> |
  <a href="#enus">🇺🇸 English (US)</a>
</p>

---

## <a id="ptbr"></a>🇧🇷 Português (BR)

> **Observação:** Este repositório refere-se à versão **v2025.11.26.0** do 📚 Projeto Lúmen. Apoie o projeto e adquira a versão paga através do link: [Instalar via Microsoft Store](https://apps.microsoft.com/detail/9N70CLLMVRPN)

<details>
<summary>Clique para expandir o README em português</summary>

# 📚 Lúmen

Versão: v2025.11.26.0  
Autor: Fernando Nillsson Cidade

Aplicativo de estudo personalizado para pessoas neurodivergentes (Dislexia, TDAH, TEA).

## 🎯 Objetivo
Fornecer uma ferramenta desktop configurável que reduza barreiras de leitura, atenção e organização para jovens e adultos neurodivergentes, oferecendo TTS local, ajustes tipográficos, gestores de tarefa e recursos para revisão ativa (mapas mentais / Método Feynman).

## 🎯 Funcionalidades principais

### 📖 Leitor Acessível
- Conversão de texto em fala (TTS) com seleção de voz, controle de velocidade e volume.
- Extração de texto de PDFs (quando disponível).
- Régua de foco para leitura linha a linha.
- Controles persistentes de fonte e tamanho.

### ⏱️ Gestão de Tempo e Tarefas
- Timer Pomodoro customizável.
- Matriz de Eisenhower para priorização.
- Rastreamento de sessões e pomodoros por tarefa.

### 🧠 Mapas Mentais e Método Feynman
- Editor de mapas mentais e conectividade entre ideias.
- Espaço guiado para explicação/auto‑teste (Método Feynman).
- Exportação de dados e imagens.

### Outros
- Importação/exportação local: PDF, JSON e formatos de texto.
- Localização: pt-BR e en-US (arquivos .ts incluídos; gerar .qm antes do empacotamento).
- Armazenamento local por padrão (privacidade).

## 🚀 Instalação (Windows — desenvolvimento)
Requisitos mínimos:
- Python 3.10+
- Git (opcional)

Passos (PowerShell recomendado):
1. Clonar repositório:
   git clone <URL-do-repositório>
2. Criar ambiente virtual:
   python -m venv .venv
3. Ativar (PowerShell):
   .\.venv\Scripts\Activate.ps1
   (ou no CMD: .\.venv\Scripts\activate.bat)
4. Instalar dependências:
   pip install -r requirements.txt
5. Executar em desenvolvimento:
   python main.py

Observação: se o sistema exige permissões de execução do PowerShell, ajuste a política de execução conforme necessário.

## 📦 Empacotamento para distribuição (Windows)
- Recomendado: PyInstaller (ou Nuitka). Incluir assets/ e language/translations/ nas 'datas' do .spec.
- Gerar arquivos de tradução .qm com:
  pyside6-lrelease language/translations/*.ts
- Incluir arquivos de licença/aviso no bundle:
  assets/EULA/, assets/NOTICES/, assets/COPYRIGHT/, assets/CLC/, assets/PRIVACY_POLICY/
- Se empacotar PySide6, documente conformidade LGPL conforme assets/NOTICES/NOTICE_pt_BR.txt.
- Testar a pasta do executável quanto a DLLs substituíveis e procedimentos de redistribuição (LGPL).

## ⚙️ Dependências (principais)
- PySide6
- pyttsx3 (ou outro backend TTS configurável)
- PyMuPDF (fitz) — extração de texto de PDFs
Consulte requirements.txt para a lista completa e versões.

## 🛠️ Notas técnicas
- Logging: utils/LogManager.py (logs em %LOCALAPPDATA%\TEA_TDAH_Dislexia).
- Dados de usuário (tarefas, mapas, histórico, configurações, arquivos temporários e logs) são salvos em:
  %LOCALAPPDATA%\TEA_TDAH_Dislexia
- Traduções: arquivos .ts em language/translations/ — gerar .qm antes do empacotamento.
- Recomenda‑se adicionar testes unitários para TTS, exportação e gerenciamento de tarefas.

## ⚠️ Limitações e recomendações
- Versão inicial: alfa/experimental — pode conter stubs e fluxos incompletos.
- Faça backup dos dados antes de atualizar ou alterar bibliotecas do executável.
- Validação de entradas (formatos numéricos, campos obrigatórios) pode precisar de reforço em algumas telas.

## 🔒 Privacidade e licença
- O aplicativo opera localmente por padrão e não envia telemetria automática.
- Para detalhes sobre tratamento de dados e consentimento, consulte:
  assets/PRIVACY_POLICY/Privacy_Policy_pt_BR.txt
- Termos de uso e restrições: assets/EULA/EULA_pt_BR.txt
- Avisos de terceiros e licenças: assets/NOTICES/NOTICE_pt_BR.txt
- Direitos autorais e marca: assets/COPYRIGHT/AVISO DE COPYRIGHT E MARCA REGISTRA_pt_BR.txt
- Contratos comerciais: assets/CLC/CLC_pt_BR.txt

## 🔗 Atalhos úteis
- Ctrl+1 — Leitor Acessível
- Ctrl+2 — Gestão de Tempo
- Ctrl+3 — Mapas Mentais
- Ctrl+4 — Método Feynman
- ESC — Fechar régua de foco

## 🧪 Testes e contribuição
- Bugs e contribuições: abrir issue / pull request no repositório (ver README online).
- Sugerido: incluir testes automatizados e CI para builds e empacotamento.

## 📞 Contato
Autor: Fernando Nillsson Cidade  
E‑mail (privacidade/licenças): linceu_lighthouse@outlook.com

## 📄 Versão e notas de lançamento
Consulte assets/RELEASE/RELEASE\ NOTES_pt_BR.txt e assets/RELEASE/RELEASE\ NOTES_en_US.txt para histórico de versões e mudanças importantes.

---

</details>

## <a id="enus"></a>🇺🇸 English (US)

> **Note:** This repository refers to the **v2025.11.26.0** version of the 📚 Lúmen Project. Support the project and purchase the paid version through the link: [Instalar via Microsoft Store](https://apps.microsoft.com/detail/9N70CLLMVRPN)

<details>
<summary>Click to expand the README in English</summary>

# 📚 Lúmen

Version: v2025.11.26.0  
Author: Fernando Nillsson Cidade

Personalized study application for neurodivergent people (Dyslexia, ADHD, ASD).

## 🎯 Objective
Provide a configurable desktop tool that reduces barriers to reading, attention and organization for neurodivergent youth and adults, offering local TTS, typographic adjustments, task managers and resources for active review (mind maps / Feynman Technique).

## 🎯 Main features

### 📖 Accessible Reader
- Text‑to‑speech (TTS) conversion with voice selection, speed and volume control.
- PDF text extraction (when available).
- Focus ruler for line‑by‑line reading.
- Persistent font and size controls.

### ⏱️ Time and Task Management
- Customizable Pomodoro timer.
- Eisenhower Matrix for prioritization.
- Session and pomodoro tracking per task.

### 🧠 Mind Maps and Feynman Technique
- Mind‑map editor and connectivity between ideas.
- Guided space for explanation/self‑test (Feynman Technique).
- Data and image export.

### Others
- Local import/export: PDF, JSON and text formats.
- Localization: pt‑BR and en‑US (.ts files included; generate .qm before packaging).
- Local storage by default (privacy).

## 🚀 Installation (Windows — development)
Minimum requirements:
- Python 3.10+
- Git (optional)

Steps (PowerShell recommended):
1. Clone the repository:
   git clone <repository-URL>
2. Create virtual environment:
   python -m venv .venv
3. Activate (PowerShell):
   .\.venv\Scripts\Activate.ps1
   (or in CMD: .\.venv\Scripts\activate.bat)
4. Install dependencies:
   pip install -r requirements.txt
5. Run in development:
   python main.py

Note: if the system requires PowerShell execution permissions, adjust the execution policy as needed.

## 📦 Packaging for distribution (Windows)
- Recommended: PyInstaller (or Nuitka). Include assets/ and language/translations/ in the .spec 'datas'.
- Generate .qm translation files with:
  pyside6-lrelease language/translations/*.ts
- Include license/notice files in the bundle:
  assets/EULA/, assets/NOTICES/, assets/COPYRIGHT/, assets/CLC/, assets/PRIVACY_POLICY/
- If bundling PySide6, document LGPL compliance procedures according to assets/NOTICES/NOTICE_pt_BR.txt.
- Test the executable folder for replaceable DLLs and redistribution procedures (LGPL).

## ⚙️ Main dependencies
- PySide6
- pyttsx3 (or another configurable TTS backend)
- PyMuPDF (fitz) — PDF text extraction
See requirements.txt for the full list and versions.

## 🛠️ Technical notes
- Logging: utils/LogManager.py (logs at %LOCALAPPDATA%\TEA_TDAH_Dislexia).
- User data (tasks, maps, history, settings, temporary files and logs) are saved at:
  %LOCALAPPDATA%\TEA_TDAH_Dislexia
- Translations: .ts files in language/translations/ — generate .qm before packaging.
- It is recommended to add unit tests for TTS, export and task management.

## ⚠️ Limitations and recommendations
- Initial release: alpha/experimental — may contain stubs and incomplete flows.
- Back up your data before updating or changing executable libraries.
- Input validation (numeric formats, required fields) may need strengthening in some screens.

## 🔒 Privacy and license
- The application runs locally by default and does not send telemetry automatically.
- For details on data handling and consent, see:
  assets/PRIVACY_POLICY/Privacy_Policy_pt_BR.txt
- Terms of use and restrictions: assets/EULA/EULA_pt_BR.txt
- Third‑party notices and licenses: assets/NOTICES/NOTICE_pt_BR.txt
- Copyright and trademark: assets/COPYRIGHT/AVISO DE COPYRIGHT E MARCA REGISTRA_pt_BR.txt
- Commercial agreements: assets/CLC/CLC_pt_BR.txt

## 🔗 Useful shortcuts
- Ctrl+1 — Accessible Reader
- Ctrl+2 — Time Management
- Ctrl+3 — Mind Maps
- Ctrl+4 — Feynman Technique
- ESC — Close focus ruler

## 🧪 Testing and contribution
- Bugs and contributions: open an issue / pull request in the repository (see online README).
- Recommended: add automated tests and CI for builds and packaging.

## 📞 Contact
Author: Fernando Nillsson Cidade  
Email (privacy/licenses): linceu_lighthouse@outlook.com

## 📄 Version and release notes
See assets/RELEASE/RELEASE NOTES_pt_BR.txt and assets/RELEASE/RELEASE NOTES_en_US.txt for version history and important changes.

---

</details>
