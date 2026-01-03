# Observação

## Erro exemplo
```txt
2025-12-13 04:46:04,216 [ERROR] File_Lumen: Erro ao carregar modelo spaCy: [E050] Can't find model 'pt_core_news_sm'. It doesn't seem to be a Python package or a valid path to a data directory.
Traceback (most recent call last):
File "c:\Users\ferna\DEV\Python\Lumen\source\modules\mapa\mp_04_ProcessadorIA.py", line 21, in carregar_modelo_nlp
self.nlp = spacy.load("pt_core_news_lg")
~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
File "C:\Users\ferna\DEV\Python\Lumen.venv\Lib\site-packages\spacy_init.py", line 52, in load
return util.load_model(
~~~~~~~~~~~~~~~^
name,
^^^^^
...<4 lines>...
config=config,
^^^^^^^^^^^^^^
)
^
File "C:\Users\ferna\DEV\Python\Lumen.venv\Lib\site-packages\spacy\util.py", line 531, in load_model
raise IOError(Errors.E050.format(name=name))
OSError: [E050] Can't find model 'pt_core_news_lg'. It doesn't seem to be a Python package or a valid path to a data directory.
```

## Correção recomendada
Instalar os modelos spaCy necessários (recomendado via comando abaixo):

```powershell
.venv\Scripts\python.exe -m spacy download pt_core_news_sm
.venv\Scripts\python.exe -m spacy download en_core_web_sm
# Opcionalmente, instalar modelos grandes:
.venv\Scripts\python.exe -m spacy download pt_core_news_lg
.venv\Scripts\python.exe -m spacy download en_core_web_lg
```

## Bibliotecas fixas (não atualizar)
- catalogue==2.0.10
- preshed==3.0.12
- thinc==8.3.10

## Bibliotecas que podem ser atualizadas (com cuidado)
- huggingface-hub==0.36.0
- huggingface-hub==1.2.3
- numpy==2.3.5
- numpy==2.4.0
- pdfminer.six==20251107
- pdfminer.six==20251230
- pillow==12.0.0
- pillow==12.1.0
- pyparsing==3.2.5
- pyparsing==3.3.1
- pypdf==6.4.2
- pypdf==6.5.0
- reportlab==4.4.6
- reportlab==4.4.7
- sentence-transformers==2.2.2
- sentence-transformers==5.2.0
- typer-slim==0.20.1
- typer-slim==0.21.0
- uvicorn==0.38.0
- uvicorn==0.40.0

## Observações
- Instalar os modelos spaCy resolve o erro de carregamento do ProcessadorIA.
- Atualizações de dependências devem ser testadas cuidadosamente por compatibilidade.
