# Origens das imagens dos manuscritos

Lista das fontes de onde vêm (ou podem vir) as imagens de manuscritos para a
Bisa. Ver também [`metadata.md`](metadata.md) — a identidade canónica de cada
imagem vive na fonte de origem e é mutável (os códigos/links mudam quando os
arquivos migram), por isso o âncora fiável é o hash da imagem.

## Portais agregadores (índices que apontam para os arquivos)

- **tombo.pt** — https://tombo.pt/ — índice curado de **registos paroquiais
  portugueses** para genealogia, organizado por Distrito → Concelho → Freguesia.
  Não aloja imagens; liga para DigitARQ, Torre do Tombo e FamilySearch.
- **etombo.pt** — *descontinuado* — antigo agregador de links; os apontadores
  partiram com as migrações do DigitARQ.

## Arquivos de origem (onde estão as imagens)

- **DigitARQ** — https://digitarq.arquivos.pt/ — plataforma da DGLAB usada pela
  Torre do Tombo e pelos arquivos distritais. Tem código de referência ISAD(G),
  permalinks (`/details?id=…` / `/documentDetails/…`) e OAI-PMH.
- **Arquivo Nacional Torre do Tombo (ANTT)** — https://antt.dglab.gov.pt/ —
  acervo nacional (também via DigitARQ; referências `PT/TT/…`).
- **FamilySearch** — https://www.familysearch.org/ — registos paroquiais e civis
  digitalizados (identificadores por filme/DGS + imagem; URLs com "ark:").
- **DGLAB** — https://arquivos.dglab.gov.pt/ — entidade que gere os arquivos e o
  DigitARQ.

### Arquivos Distritais (instâncias DigitARQ próprias)

Cada distrito tem o seu arquivo/DigitARQ. Códigos de referência começam por
`PT/AD<dist>/…` (ex.: `PT/ADVIS/…` = Arquivo Distrital de Viseu, como no exemplo
`PT-ADVIS-AC-GCVIS-H-D-001-01016_m0003`).

| Distrito | Código | Arquivo |
|---|---|---|
| Aveiro | ADAVR | Arquivo Distrital de Aveiro |
| Beja | ADBJA | Arquivo Distrital de Beja |
| Braga | ADBRG | Arquivo Distrital de Braga |
| Bragança | ADBGC | Arquivo Distrital de Bragança |
| Castelo Branco | ADCTB | Arquivo Distrital de Castelo Branco |
| Coimbra | ADCBR | Arquivo Distrital de Coimbra |
| Évora | ADEVR | Arquivo Distrital de Évora |
| Faro | ADFAR | Arquivo Distrital de Faro |
| Guarda | ADGRD | Arquivo Distrital da Guarda |
| Leiria | ADLRA | Arquivo Distrital de Leiria |
| Lisboa | ADLSB | Arquivo Distrital de Lisboa |
| Portalegre | ADPTG | Arquivo Distrital de Portalegre |
| Porto | ADPRT | Arquivo Distrital do Porto |
| Santarém | ADSTR | Arquivo Distrital de Santarém |
| Setúbal | ADSTB | Arquivo Distrital de Setúbal |
| Viana do Castelo | ADVCT | Arquivo Distrital de Viana do Castelo |
| Vila Real | ADVRL | Arquivo Distrital de Vila Real |
| Viseu | ADVIS | Arquivo Distrital de Viseu |
| Açores | — | Arquivos regionais dos Açores |
| Madeira | ABM | Arquivo Regional e Biblioteca Pública da Madeira |

> Os códigos seguem a convenção da DGLAB; confirmar caso a caso no DigitARQ do
> distrito, já que algumas instâncias e códigos mudam com as migrações.

## Notas para a importação

- Guardar sempre o **URL de origem** e o **código de referência**, mas tratar o
  **hash da imagem** como identidade fiável.
- Atenção a marcas de água (ex.: "DigitArq") e a hotlinking/embargos — algumas
  imagens não são diretamente apresentáveis e exigem abrir a página do arquivo.
