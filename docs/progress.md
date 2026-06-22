# Bisa — o que já foi feito

Resumo do estado do projeto. Companheiro de [`plan.md`](plan.md) (HTR),
[`metadata.md`](metadata.md) (modelo de dados) e [`sources.md`](sources.md)
(origens das imagens).

## Visão geral

**Bisa** ajuda pessoas a investigar a sua árvore genealógica em Portugal:
transcreve documentos manuscritos e extrai relações familiares. Tem três partes
no mesmo repositório (`pytombo`):

- **Site público** (Django) — página inicial em português para investigadores.
- **Admin de especialistas** (Django admin) — onde se transcrevem manuscritos.
- **Ferramenta de OCR** (Streamlit) — leitura assistida de imagens/texto.

## Infraestrutura

- Gestão de dependências com **uv** (`pyproject.toml`, `uv.lock`).
- Alojado no servidor Hetzner partilhado (46.224.236.207), atrás de **Caddy**
  (HTTPS automático). Detalhes em [`../deploy/NOTES.md`](../deploy/NOTES.md).
- **Domínio:** https://bisa.filias.dev (o antigo `tombo.filias.dev` foi
  descontinuado).
  - `/` → site Django · `/admin/` → admin · `/st/` → Streamlit.
- Serviços systemd: `pytombo` (Streamlit), `pytombo-web` (Django/gunicorn),
  `pytombo-webhook` (deploy).
- **Deploy automático** por webhook do GitHub no push para `main`
  (git pull → uv sync → migrate → collectstatic → restart).
  - ⚠️ Pendente: o URL do webhook no GitHub tem de passar para
    `https://bisa.filias.dev/deploy` (tarefa do admin do repositório). Até lá,
    o deploy é feito manualmente.

## Aplicação web (Django, em `web/`)

- Projeto `config`; apps `pages` (site) e `manuscripts` (dados + admin).
- Base de dados **SQLite** (suficiente nesta fase; pronto para Postgres via
  `DATABASE_URL`).
- Estáticos servidos por **WhiteNoise**; imagens carregadas em `/media/`.

### Modelo de dados (fase 1)
- `Manuscript` — imagem/URL do manuscrito + metadados. Âncora de
  correspondência imutável `image_sha256`; `reference_code`/`image_no`
  extraídos; `raw_metadata`, `metadata_source`, `verified`. Ver
  [`metadata.md`](metadata.md).
- `Transcription` — texto do especialista, `status` (rascunho/revisão/aprovada),
  `transcriber`. Cada transcrição aprovada é um par de treino (imagem → texto)
  para o HTR.
- Comando `backfill_manuscripts` — calcula hashes e extrai referências, sem
  destruir dados verificados.

### Área de transcrição (admin)
- Formulário único: **URL do manuscrito + caixa de texto + Gravar**.
- **Pré-visualização lado a lado**: manuscrito à esquerda (imagem inline, ou
  botão "Abrir manuscrito" para páginas de visualizador), transcrição à direita;
  painel do manuscrito fixo (sticky) enquanto se escreve.
- O especialista autenticado fica registado como `transcriber`.

## Por fazer (próximos passos)

- Mudar o URL do webhook do GitHub para `bisa.filias.dev/deploy`.
- Contas de especialista (não-superuser) com acesso só à transcrição.
- Conteúdo real da página pública (Como começar, Arquivos, etc.).
- Fase 2 do modelo: hierarquia `Archive`/`Document`, pHash, fila de revisão.
- Importador idempotente de manuscritos a partir das origens.
