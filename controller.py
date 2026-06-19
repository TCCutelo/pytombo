class Controller:
    def preparar_imagem(self, nome_ficheiro, output=None):
        from model.Image_preprocessor import Image_preprocessor

        ip = Image_preprocessor(nome_ficheiro)
        ip.preparar_imagem(output)
        return ip.get_ficheiro_preparado()

    def ler_imagem(self, nome_ficheiro, backend="openai"):
        from model.Ocr_reader import Ocr_reader

        ocr = Ocr_reader(nome_ficheiro, backend)
        ocr.ler_documento()
        transcricao = ocr.get_transcricao()
        return self.extrair_relacoes(transcricao)

    def ler_texto(self, nome_ficheiro):
        from model.Data_loader import Data_loader

        dl = Data_loader(nome_ficheiro)
        dl.carregar_ficheiro()
        texto = dl.get_texto()
        return self.extrair_relacoes(texto)

    def extrair_relacoes(self, texto):
        from model.Relation_extractor import Relation_extractor

        re = Relation_extractor(texto)
        re.extrair_relacoes()
        return texto, re.get_relacoes()
