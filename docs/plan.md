# Plano: HTR proprio para manuscritos portugueses

Plano para construir o nosso proprio sistema de transcricao (HTR — Handwritten
Text Recognition) para documentos manuscritos portugueses antigos (ex.: o
exemplo de 1918 em `artifacts/m0003_prepared.png`).

> Contexto: o Tesseract nao le cursiva antiga (devolve texto vazio neste tipo de
> documento). Os modelos de visao (OpenAI/Claude/Gemini) ja leem razoavelmente
> sem treino. Mas temos dois recursos que tornam um modelo proprio viavel:
> **imagens publicas online** (dados) e **especialistas que sabem ler** (rotulos).

## Principios

1. **Nao treinar de raiz.** Todos os caminhos sensatos fazem *fine-tune* de um
   modelo pre-treinado nos nossos documentos. "Construir o nosso" = o nosso
   modelo, treinado na nossa caligrafia, sobre uma base ja existente.
2. **O tempo dos especialistas e o recurso escasso.** Toda a estrategia deve
   minimizar horas de transcricao manual.
3. **HTR e um pipeline, nao um modelo unico.** A qualidade e limitada pela etapa
   mais fraca.

## O pipeline (3 etapas)

1. **Analise de layout / segmentacao de linhas** — detetar regioes de texto e
   linhas de base; ignorar margens, selos e a marca de agua "DigitArq". Em
   documentos de arquivo isto e frequentemente metade da dificuldade.
2. **Transcricao ao nivel da linha** — o modelo que treinamos (imagem de uma
   linha -> texto).
3. **Pos-processamento** — lexico portugues + normalizacao de grafia historica
   para limpar o resultado.

## O truque central: human-in-the-loop

Os especialistas **nao** devem transcrever a partir do zero. Fluxo correto:

1. Um modelo base (visao-LLM ou modelo publico) gera uma **primeira transcricao**.
2. Os especialistas **corrigem** (varias vezes mais rapido do que transcrever).
3. Re-treinamos com as correcoes e repetimos.
4. **Active learning**: priorizar as paginas/linhas em que o modelo tem menos
   confianca.

Definir **guidelines de transcricao** antes de comecar (abreviaturas, quebras de
linha, `[ilegivel]`, notas de margem) — caso contrario os rotulos ficam
inconsistentes e o modelo aprende o ruido.

## Dados necessarios

- Ground truth = paginas transcritas alinhadas com imagens de linha
  (formato PAGE-XML / ALTO; as ferramentas abaixo produzem isto).
- Volume aproximado:
  - ~25–75 paginas (~5–15k palavras) de uma **caligrafia consistente** -> modelo
    utilizavel.
  - 100+ paginas -> modelo forte.
  - Mais, se quisermos generalizar para muitos escribas.

## Caminhos de construcao

### A. Modelo personalizado no Transkribus (gerido)
- Plataforma treina por nos; nos fornecemos as transcricoes.
- Pouca experiencia de ML necessaria; sem infraestrutura propria (cloud + creditos).
- Mais rapido a obter resultados; menos controlo e custo continuo.

### B. Stack open-source self-hosted
- eScriptorium + **Kraken**, ou **TrOCR** (fine-tune via HuggingFace).
- Experiencia de ML media/alta; precisa de GPU para treino (inferencia mais leve).
- Controlo total: o modelo e os dados sao nossos.

### C. (Ambicioso) Fine-tune de um vision-LLM aberto
- Ex.: modelo da familia Qwen2-VL, treinado em pares (imagem, transcricao).
- Maior teto de qualidade, mais compute e experiencia; modelo totalmente nosso.

| Criterio | A. Transkribus | B. Open self-hosted | C. VLM fine-tune |
|---|---|---|---|
| Experiencia ML | Baixa | Media/alta | Alta |
| Infraestrutura | Nenhuma | GPU treino | GPU (mais) |
| Controlo/posse | Menor | Total | Total |
| Tempo ao 1.o modelo | Dias–semanas | Semanas–meses | Meses |
| Melhor quando | Resultados rapidos | Privacidade/controlo | Teto maximo |

## Como medir

- Metrica principal: **CER (Character Error Rate)** num conjunto de teste
  reservado (paginas que o modelo nunca viu).
- Referencia: ~5–10% CER = util numa caligrafia consistente; <5% = excelente.
- Tambem util: WER (Word Error Rate).

## Integracao na app

O design MVC ja isola isto: o modelo treinado torna-se mais um backend do
`Ocr_reader` — `backend="custom"` a chamar o nosso endpoint de inferencia (ou a
API do Transkribus). O setup de Streamlit/webhook/deploy nao muda.

## Roadmap por fases

### Fase 0 — Bootstrap (esta semana)
- Adicionar um backend de visao-LLM para a **primeira transcricao**.
- Objetivo duplo: valor imediato + gerar rascunhos de rotulos.

### Fase 1 — Primeiros rotulos
- Escrever as **guidelines de transcricao**.
- Especialistas corrigem algumas dezenas de paginas -> primeiro ground truth.

### Fase 2 — Primeiro modelo
- Comecar com Transkribus (mais rapido para provar que funciona).
- Avaliar CER num conjunto de teste reservado.

### Fase 3 — Iterar
- Loop pre-label -> corrigir -> re-treinar, com active learning.
- Decidir se passamos para stack self-hosted (Kraken/TrOCR) para posse total.

### Fase 4 — Producao
- Expor o modelo como backend `custom` na app.
- Monitorizar qualidade; reciclar correcoes para treino continuo.

## Decisoes em aberto

- [ ] Provider do visao-LLM para bootstrap (OpenAI / Claude / Gemini).
- [ ] Gerido (Transkribus) vs self-hosted (Kraken/TrOCR) para o modelo proprio.
- [ ] Fonte e licenca das imagens publicas (que arquivos/coleccoes).
- [ ] Disponibilidade dos especialistas (horas/semana) e formato de entrega.
- [ ] Infraestrutura de treino (GPU cloud vs local) se formos self-hosted.

## Proximos passos concretos

1. Escolher provider para o bootstrap e ativar o backend na app.
2. Redigir as guidelines de transcricao.
3. Selecionar o primeiro lote de paginas (caligrafia consistente) para rotular.
