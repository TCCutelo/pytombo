# Metadados dos manuscritos e estrategia de correspondencia

Como guardar os metadados dos manuscritos e como associar (match) cada imagem
ao registo certo na base de dados sem corromper os dados. Companheiro de
[`plan.md`](plan.md).

## De onde vêm os manuscritos

As imagens vêm de **registos paroquiais portugueses** indexados por sites como
[tombo.pt](https://tombo.pt/) (e o antigo etombo, hoje inativo). Pontos-chave:

- Estes sites **não guardam as imagens** — apenas **apontam (links)** para os
  arquivos reais: **DigitARQ** (arquivos distritais), **Torre do Tombo** e
  **FamilySearch**.
- A identidade canónica de cada imagem vive no **arquivo de origem**, não no
  tombo.pt nem no nome do ficheiro.
- Essas identidades são **mutáveis**: quando um arquivo migra de versão do
  DigitARQ, os códigos de referência e os URLs mudam e os links partem (foi o
  que matou o etombo).

O nome de ficheiro `PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003.jpg` descodifica-se em:

| Parte | Significado |
|---|---|
| `PT` | Portugal |
| `ADVIS` | Arquivo Distrital de Viseu (o **arquivo**) |
| `...GCVIS-H-D-001-01016` | **código de referência** ISAD(G) (a unidade/livro) |
| `_m0003` | **número da imagem/fólio** dentro da unidade |

Ou seja, o nome do ficheiro **contém** bom sinal — mas é derivado e mutável.
Por isso **extraímos** essa informação para campos estruturados; **não** a usamos
como identidade.

## Princípio central: separar identidade interna de identificadores externos

É isto que evita "estragar os dados":

1. **A chave interna (surrogate) é a única identidade estável.** O `id` da linha
   é a quem as transcrições e tudo o resto apontam. Códigos de referência e URLs
   externos são **atributos que podem mudar** — nunca chave primária.
2. **Guardar vários âncoras externos, por ordem de estabilidade**, para um
   registo continuar a ser correspondível mesmo quando um deles parte:
   - **`image_sha256`** — hash dos bytes da imagem **original**. Imutável,
     imune a renomeações e a mudanças de URL. O âncora mais fiável; usado para
     deduplicação e re-correspondência. (Hash da original, não da pré-processada.)
   - *(futuro)* **perceptual hash (pHash)** — apanha o **mesmo fólio
     re-exportado** noutra resolução/compressão, onde o SHA-256 já difere.
   - **arquivo + código de referência + número da imagem** (estruturado, extraído
     do nome/scrape) — chave natural legível.
   - **URL/permalink de origem** (DigitARQ `documentDetails/[id]`, ark do
     FamilySearch, página tombo.pt) + ID numérico externo.
3. **Nunca perder os metadados originais.** Guardar um blob `raw_metadata` (JSON)
   tal como foi recebido, ao lado dos campos normalizados. Registar a
   **proveniência** (`metadata_source`: filename / scraped / manual / digitarq) e
   um campo `verified`.
4. **Importações idempotentes e não destrutivas.** Corresponder cada imagem nova
   por hash → referência+nº imagem → URL (nesta prioridade). Match único →
   enriquecer (mas **nunca sobrescrever campos verificados por especialistas**);
   sem match → criar; ambíguo/múltiplo → **fila de revisão humana**, sem fundir
   automaticamente. Registar todas as ações (audit trail).

## Modelo de dados (alvo)

Hierarquia arquivística (um livro → muitas imagens → uma+ transcrições):

- **`Archive`** — `code` (PT/ADVIS), `name`, `system`
  (digitarq / torre_do_tombo / familysearch), `base_url`.
- **`Document`** (livro / unidade) — `archive` (FK), `reference_code` (ISAD),
  `title`, `document_type` (baptismo/casamento/óbito/…), `date_start`,
  `date_end`, `freguesia`, `concelho`, `distrito`, `source_url`, `external_id`,
  `raw_metadata` (JSON), `notes`.
- **`Manuscript`** (a imagem — o que se transcreve) — `document` (FK), `image`,
  `image_no` (m0003), **`image_sha256` (único)**, `phash`, `source_image_url`,
  `raw_metadata` (JSON), `metadata_source`, `verified`, timestamps.
  - único: `image_sha256`; único-junto: (`document`, `image_no`).
- **`Transcription`** — inalterado, FK → `Manuscript`. Cada uma aprovada continua
  a ser um par de treino (imagem → texto) para o HTR.

Cadeia: `Transcription → Manuscript(imagem) → Document(livro) → Archive`.

## Faseamento

Não é preciso construir tudo de uma vez.

### Fase 1 (implementada agora) — proteger os dados no modelo atual
Adicionar ao `Manuscript`:
- `image_sha256` (único) — âncora de deduplicação.
- `reference_code` + `image_no` — partes estruturadas extraídas do nome.
- `raw_metadata` (JSON) — metadados originais, nunca perdidos.
- `metadata_source` + `verified` — proveniência e confirmação humana.

E um comando de gestão `backfill_manuscripts` que:
- calcula o SHA-256 das imagens existentes (deteta colisões/duplicados),
- extrai `reference_code` + `image_no` do `reference`/nome do ficheiro,
- **nunca** toca em registos `verified`,
- suporta `--dry-run` e regista um resumo.

### Fase 2 — hierarquia completa
Refatorar para `Archive` / `Document` via migração, assim que o fluxo de
importação estiver provado. Acrescentar pHash e a fila de revisão de matches
ambíguos.

### Fase 3 — importador
Pipeline idempotente (hash → referência → URL) com enriquecimento não destrutivo
e audit trail.

## A confirmar

Abrir **um documento real no tombo.pt** e registar exatamente que campos mostra e
como é o link de saída para o arquivo — isso diz-nos que campos `raw_metadata`
conseguimos capturar por cada origem (DigitARQ / Torre do Tombo / FamilySearch).
