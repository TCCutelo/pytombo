# TTombo MVC

Projeto Python simples, em formato Model View Controller, para ajudar a transcrever documentos manuscritos portugueses e extrair relacoes familiares simples, por exemplo:

```text
Antonio Coutello solteiro, filho de Manoel Coutello e de Eufemia ...
```

Saida esperada:

```json
{
  "child": "Antonio Coutello",
  "father": "Manoel Coutello",
  "mother": "Eufemia"
}
```

## Limites reais

Sim, e possivel fazer isto, mas documentos manuscritos antigos raramente funcionam bem com OCR classico sem revisao humana. O fluxo mais fiavel e:

1. melhorar a imagem;
2. obter uma transcricao por um backend de OCR/visao;
3. corrigir a transcricao quando necessario;
4. extrair nomes e relacoes com regras;
5. exportar JSON/CSV para analise genealogica.

## Estrutura

```text
TTombo/
├── main.py
├── view.py
├── controller.py
├── model/
│   ├── Data_loader.py
│   ├── Image_preprocessor.py
│   ├── Ocr_reader.py
│   └── Relation_extractor.py
├── artifacts/
├── transcricao_exemplo.txt
└── README.md
```

## Instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se fores usar apenas ficheiros de texto ja transcritos, nao precisas instalar nada extra.

Se neste computador o comando `python` nao funcionar, podes usar `uv`:

```powershell
uv venv
.\.venv\Scripts\Activate.ps1
uv pip install -r requirements.txt
```

## Usar com transcricao ja existente

```powershell
python main.py --texto transcricao_exemplo.txt --json
```

Neste computador tambem podes usar:

```powershell
uv run python main.py --texto transcricao_exemplo.txt --json
```

## Usar a aplicacao

```powershell
uv run streamlit run app.py
```

A aplicacao permite carregar uma transcricao em `.txt`, escrever texto manualmente ou submeter uma imagem.

## Usar com imagem e Tesseract

O Tesseract pode falhar bastante em escrita cursiva antiga, mas serve como baseline.

```powershell
python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --backend tesseract --json
```

## Usar com backend OpenAI

Define uma chave de API e escolhe o modelo por variavel de ambiente. Isto e normalmente melhor para manuscritos que OCR classico.

```powershell
$env:OPENAI_API_KEY="..."
$env:TTOMBO_OPENAI_MODEL="gpt-4.1-mini"
python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --backend openai --json
```

## Preparar uma imagem

```powershell
python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --preprocessar --output artifacts\m0003_prepared.png
```
