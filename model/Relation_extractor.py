import re
import unicodedata
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Family_relation:
    child: str
    father: str
    mother: str
    evidence: str
    confidence: float

    def to_dict(self):
        return asdict(self)


class Relation_extractor:
    def __init__(self, texto):
        self.__texto = texto
        self.__relacoes = []

    def get_texto(self):
        return self.__texto

    def set_texto(self, novo_texto):
        self.__texto = novo_texto

    def get_relacoes(self):
        return self.__relacoes

    def extrair_relacoes(self):
        try:
            self.__relacoes = self.__extract_family_relations(self.__texto)
            print("Extracao de relacoes OK")
        except Exception as e:
            print(f"Erro...{e}")

    def __extract_family_relations(self, texto):
        texto = self.__normalizar_texto(texto)
        relacoes = []
        padrao = re.compile(r"\bfilh[oa]\s+d[eoa]\s+", flags=re.IGNORECASE)

        for match in padrao.finditer(texto):
            antes = texto[: match.start()].strip(" ,.")
            depois = texto[match.end() :].strip()
            filho = self.__ultima_pessoa(antes)
            pai, mae, evidencia = self.__pais(depois)

            if filho and pai and mae:
                relacoes.append(
                    Family_relation(
                        child=filho,
                        father=pai,
                        mother=mae,
                        evidence=evidencia,
                        confidence=self.__confianca(filho, pai, mae),
                    )
                )

        return relacoes

    def __normalizar_texto(self, texto):
        texto = unicodedata.normalize("NFKC", texto)
        texto = texto.replace("\n", " ")
        texto = texto.replace(";", ",")
        return re.sub(r"\s+", " ", texto).strip()

    def __ultima_pessoa(self, texto):
        for parte in reversed(re.split(r"[,.]", texto)):
            palavras = parte.strip().split()
            if len(palavras) > 6:
                palavras = palavras[-6:]

            while palavras and self.__e_descricao(palavras[-1]):
                palavras.pop()

            while palavras and self.__e_descricao(palavras[0]):
                palavras.pop(0)

            nome = self.__limpar_nome(" ".join(palavras))
            if nome:
                return nome

        return ""

    def __pais(self, texto):
        evidencia = texto[:240].strip()
        padrao = re.compile(
            r"(?P<pai>.+?)\s+e\s+d[aeo]\s+(?P<mae>.+?)(?=,|\.|\s+\b(?:natural|morador|moradora|residente|freguesia|concelho|distrito)\b|$)",
            flags=re.IGNORECASE,
        )
        match = padrao.search(texto)
        if not match:
            return "", "", evidencia

        pai = self.__limpar_nome(match.group("pai"))
        mae = self.__limpar_nome(match.group("mae"))
        return pai, mae, evidencia

    def __limpar_nome(self, nome):
        nome = re.sub(r"^(?:diz|digo|declara|declarou)\s+", "", nome.strip(), flags=re.IGNORECASE)
        nome = re.sub(r"\b(?:de|do|da|dos|das)$", "", nome.strip(), flags=re.IGNORECASE)
        nome = re.sub(r"^[,.\-\s]+|[,.\-\s]+$", "", nome)
        return re.sub(r"\s+", " ", nome)

    def __e_descricao(self, palavra):
        descricoes = {
            "natural",
            "morador",
            "moradora",
            "residente",
            "freguesia",
            "concelho",
            "distrito",
            "solteiro",
            "solteira",
            "casado",
            "casada",
            "viuvo",
            "viuva",
            "lavrador",
            "jornaleiro",
        }
        palavra = unicodedata.normalize("NFKD", palavra.lower())
        palavra = "".join(letra for letra in palavra if not unicodedata.combining(letra))
        palavra = re.sub(r"[^a-z]", "", palavra)
        return palavra in descricoes

    def __confianca(self, filho, pai, mae):
        score = 0.55
        if len(filho.split()) >= 2:
            score += 0.15
        if len(pai.split()) >= 2:
            score += 0.15
        if mae:
            score += 0.15
        return min(score, 0.95)
