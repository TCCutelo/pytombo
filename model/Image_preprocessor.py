from pathlib import Path

from PIL import Image, ImageOps


class Image_preprocessor:
    def __init__(self, nome_ficheiro):
        self.__nome_ficheiro = nome_ficheiro
        self.__ficheiro_preparado = None

    def get_nome_ficheiro(self):
        return self.__nome_ficheiro

    def set_nome_ficheiro(self, novo_nome):
        self.__nome_ficheiro = novo_nome

    def get_ficheiro_preparado(self):
        return self.__ficheiro_preparado

    def preparar_imagem(self, output=None):
        try:
            input_path = Path(self.__nome_ficheiro)
            if output is None:
                output = input_path.with_name(f"{input_path.stem}_prepared.png")

            output_path = Path(output)
            image = Image.open(input_path)
            image = ImageOps.exif_transpose(image)
            image = ImageOps.grayscale(image)
            image = ImageOps.autocontrast(image, cutoff=1)
            image.save(output_path)

            self.__ficheiro_preparado = output_path
            print("Preparacao da imagem OK")
        except Exception as e:
            print(f"Erro...{e}")
