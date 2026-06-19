import base64
import os
from pathlib import Path


PROMPT = (
    "Transcreve este documento manuscrito antigo em portugues. "
    "Mantem nomes proprios e grafia provavel. "
    "Quando houver duvida, usa [ilegivel]. "
    "Depois devolve apenas a transcricao, sem comentario."
)


class Ocr_reader:
    def __init__(self, nome_ficheiro, backend="openai"):
        self.__nome_ficheiro = nome_ficheiro
        self.__backend = backend
        self.__transcricao = ""

    def get_nome_ficheiro(self):
        return self.__nome_ficheiro

    def set_nome_ficheiro(self, novo_nome):
        self.__nome_ficheiro = novo_nome

    def get_backend(self):
        return self.__backend

    def set_backend(self, novo_backend):
        self.__backend = novo_backend

    def get_transcricao(self):
        return self.__transcricao

    def ler_documento(self):
        try:
            if self.__backend == "openai":
                self.__transcricao = self.__ler_com_openai()
            elif self.__backend == "tesseract":
                self.__transcricao = self.__ler_com_tesseract()
            else:
                raise ValueError(f"Backend desconhecido: {self.__backend}")
            print("Transcricao OK")
        except Exception as e:
            print(f"Erro...{e}")
            raise

    def __ler_com_openai(self):
        from openai import OpenAI

        caminho = Path(self.__nome_ficheiro)
        imagem_base64 = base64.b64encode(caminho.read_bytes()).decode("ascii")
        media_type = self.__media_type(caminho)
        modelo = os.getenv("TTOMBO_OPENAI_MODEL", "gpt-4.1-mini")

        client = OpenAI()
        response = client.responses.create(
            model=modelo,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": PROMPT},
                        {
                            "type": "input_image",
                            "image_url": f"data:{media_type};base64,{imagem_base64}",
                        },
                    ],
                }
            ],
        )
        return response.output_text.strip()

    def __ler_com_tesseract(self):
        import pytesseract

        return pytesseract.image_to_string(self.__nome_ficheiro, lang="por")

    def __media_type(self, caminho):
        extensao = caminho.suffix.lower()
        if extensao in [".jpg", ".jpeg"]:
            return "image/jpeg"
        if extensao == ".png":
            return "image/png"
        if extensao == ".webp":
            return "image/webp"
        return "application/octet-stream"
