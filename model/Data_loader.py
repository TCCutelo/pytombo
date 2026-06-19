from pathlib import Path


class Data_loader:
    def __init__(self, nome_ficheiro):
        self.__nome_ficheiro = nome_ficheiro
        self.__texto = ""

    def get_nome_ficheiro(self):
        return self.__nome_ficheiro

    def set_nome_ficheiro(self, novo_nome):
        self.__nome_ficheiro = novo_nome

    def get_texto(self):
        return self.__texto

    def carregar_ficheiro(self):
        try:
            caminho = Path(self.__nome_ficheiro)
            self.__texto = caminho.read_text(encoding="utf-8")
            print("Carregamento do texto OK")
        except Exception as e:
            print(f"Erro...{e}")
