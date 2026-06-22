# Bisa

> Antes "TTombo". O nome do projeto/repositorio interno continua `pytombo`.


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
├── pyproject.toml
└── README.md
```

## Instalar dependencias

Este projeto usa [uv](https://docs.astral.sh/uv/) para gerir dependencias. As dependencias estao declaradas no `pyproject.toml` e ficam fixadas no `uv.lock`.

```powershell
uv sync
```

O `uv sync` cria o ambiente virtual e instala tudo. Depois corre os comandos com `uv run`, sem precisares de ativar o ambiente manualmente.

## Usar com transcricao ja existente

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
uv run python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --backend tesseract --json
```

## Usar com backend OpenAI

Define uma chave de API e escolhe o modelo por variavel de ambiente. Isto e normalmente melhor para manuscritos que OCR classico.

```powershell
$env:OPENAI_API_KEY="..."
$env:TTOMBO_OPENAI_MODEL="gpt-4.1-mini"
uv run python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --backend openai --json
```

## Preparar uma imagem

```powershell
uv run python main.py --imagem "c:\Users\Utilizador\Downloads\PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg" --preprocessar --output artifacts\m0003_prepared.png
```

## Site e administracao (Django)

Em `web/` existe um projeto Django que serve o site publico e a area de
administracao onde os especialistas inserem as transcricoes dos manuscritos
(cada transcricao aprovada serve tambem de dado de treino — ver
[`docs/plan.md`](docs/plan.md)).

```powershell
# migracoes e utilizador de administracao (primeira vez)
uv run python web/manage.py migrate
uv run python web/manage.py createsuperuser

# correr o servidor de desenvolvimento
uv run python web/manage.py runserver
```

- Site publico: http://127.0.0.1:8000/
- Administracao (especialistas): http://127.0.0.1:8000/admin/

## Deploy

A aplicacao esta publicada em https://bisa.filias.dev (o antigo
https://tombo.filias.dev redireciona para la) e faz deploy automatico
quando se faz push para `main` (webhook do GitHub no servidor). Os detalhes de
infraestrutura (servico systemd, webhook, Caddy) estao em [`deploy/NOTES.md`](deploy/NOTES.md).
