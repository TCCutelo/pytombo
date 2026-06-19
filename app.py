from pathlib import Path
import os

import streamlit as st

from controller import Controller


UPLOAD_DIR = Path("artifacts") / "uploads"


def main():
    st.set_page_config(page_title="TTombo", layout="wide")
    st.title("TTombo")
    st.caption("Transcreve documentos e extrai relacoes familiares a partir do texto corrigido.")

    controller = Controller()
    if "transcricao_imagem" not in st.session_state:
        st.session_state.transcricao_imagem = ""
    if "imagem_carregada" not in st.session_state:
        st.session_state.imagem_carregada = None

    tab_imagem, tab_texto = st.tabs(["1. Imagem para transcricao", "2. Texto ja transcrito"])

    with tab_imagem:
        st.subheader("Passo 1 - Carregar imagem")
        imagem = st.file_uploader(
            "Documento",
            type=["jpg", "jpeg", "png", "webp"],
            help="Escolhe uma imagem do documento. Formatos aceites: JPG, PNG ou WEBP.",
        )

        if imagem is not None:
            st.session_state.imagem_carregada = imagem.name
            st.success(f"Imagem carregada: {imagem.name}")
            with st.expander("Ver imagem carregada", expanded=True):
                st.image(imagem, use_container_width=True)
        else:
            st.info("Comeca por fazer upload da imagem do documento.")

        st.subheader("Passo 2 - Escolher motor de leitura")
        backend = st.selectbox(
            "Motor de leitura",
            ["openai", "tesseract"],
            help="OpenAI usa a API configurada no ambiente. Tesseract usa OCR local instalado no computador.",
        )

        openai_sem_chave = backend == "openai" and not os.getenv("OPENAI_API_KEY")
        if openai_sem_chave:
            st.warning(
                "O motor OpenAI precisa da variavel OPENAI_API_KEY. "
                "Sem essa chave, a leitura do documento vai falhar."
            )
        elif backend == "tesseract":
            st.info(
                "O Tesseract nao precisa de API key, mas precisa do executavel "
                "Tesseract instalado ou configurado no computador."
            )

        st.subheader("Passo 3 - Ler documento")
        pode_ler = imagem is not None and not openai_sem_chave
        if st.button("Ler documento", type="primary", disabled=not pode_ler):
            caminho = guardar_upload(imagem)
            try:
                with st.spinner("A ler documento..."):
                    transcricao, _ = controller.ler_imagem(str(caminho), backend)
                st.session_state.transcricao_imagem = transcricao
                if transcricao.strip():
                    st.success("Documento lido. Confirma e corrige a transcricao no passo seguinte.")
                else:
                    st.warning("A leitura terminou, mas nao foi encontrado texto.")
            except Exception as exc:
                st.error(f"Nao foi possivel ler o documento: {exc}")

        if imagem is None:
            st.caption("O botao fica ativo depois de carregares uma imagem.")
        elif openai_sem_chave:
            st.caption("Configura a OPENAI_API_KEY ou escolhe outro motor de leitura.")

        st.subheader("Passo 4 - Rever transcricao")
        transcricao_corrigida = st.text_area(
            "Transcricao da imagem",
            value=st.session_state.transcricao_imagem,
            height=260,
            help="Corrige nomes, palavras ilegiveis e pontuacao antes de extrair relacoes.",
        )
        st.session_state.transcricao_imagem = transcricao_corrigida

        st.subheader("Passo 5 - Extrair relacoes")
        if st.button(
            "Extrair relacoes da transcricao corrigida",
            disabled=not transcricao_corrigida.strip(),
        ):
            analisar_texto(controller, transcricao_corrigida)

        if not transcricao_corrigida.strip():
            st.caption("Este botao fica ativo quando houver texto na transcricao.")

    with tab_texto:
        st.subheader("Passo 1 - Colar ou carregar transcricao")
        texto = st.text_area(
            "Texto transcrito",
            height=260,
            help="Usa esta aba se ja tens a transcricao pronta e queres apenas extrair relacoes.",
        )
        ficheiro_texto = st.file_uploader("Ficheiro TXT", type=["txt"])

        if ficheiro_texto is not None:
            texto = ficheiro_texto.read().decode("utf-8")
            texto = st.text_area("Conteudo do ficheiro", value=texto, height=260)

        st.subheader("Passo 2 - Extrair relacoes")
        if st.button("Extrair relacoes", type="primary", disabled=not texto.strip()):
            analisar_texto(controller, texto)
        if not texto.strip():
            st.caption("Escreve ou carrega uma transcricao para ativar a extracao.")


def analisar_texto(controller, texto):
    if not texto.strip():
        st.warning("Escreve ou carrega uma transcricao.")
        return

    transcricao, relacoes = controller.extrair_relacoes(texto)
    mostrar_resultado(transcricao, relacoes)


def guardar_upload(upload):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    caminho = UPLOAD_DIR / upload.name
    caminho.write_bytes(upload.getbuffer())
    return caminho


def mostrar_resultado(transcricao, relacoes):
    st.subheader("Transcricao")
    st.text_area("Resultado da leitura", value=transcricao, height=220)

    st.subheader("Relacoes encontradas")
    if not relacoes:
        st.info("Nenhuma relacao encontrada.")
        return

    dados = []
    for relacao in relacoes:
        dados.append(
            {
                "Pessoa": relacao.child,
                "Pai": relacao.father,
                "Mae": relacao.mother,
                "Confianca": relacao.confidence,
            }
        )

    st.dataframe(dados, use_container_width=True)


if __name__ == "__main__":
    main()
