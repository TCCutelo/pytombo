import argparse
import json

from controller import Controller


def main():
    parser = argparse.ArgumentParser(prog="ttombo-mvc")
    parser.add_argument("--imagem", help="Caminho da imagem manuscrita.")
    parser.add_argument("--texto", help="Caminho de uma transcricao em texto.")
    parser.add_argument("--backend", default="openai", choices=["openai", "tesseract"])
    parser.add_argument("--preprocessar", action="store_true")
    parser.add_argument("--output", help="Caminho para guardar a imagem preparada.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    controller = Controller()

    if args.preprocessar and args.imagem:
        ficheiro_preparado = controller.preparar_imagem(args.imagem, args.output)
        print(f"Imagem preparada: {ficheiro_preparado}")
        return

    if args.texto:
        transcricao, relacoes = controller.ler_texto(args.texto)
        mostrar_resultado(transcricao, relacoes, args.json)
        return

    if args.imagem:
        transcricao, relacoes = controller.ler_imagem(args.imagem, args.backend)
        mostrar_resultado(transcricao, relacoes, args.json)
        return

    parser.print_help()


def mostrar_resultado(transcricao, relacoes, usar_json=False):
    if usar_json:
        resultado = {
            "transcricao": transcricao,
            "relacoes": [relacao.to_dict() for relacao in relacoes],
        }
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        return

    print("Transcricao:")
    print(transcricao)
    print()
    print("Relacoes encontradas:")
    for relacao in relacoes:
        print(f"{relacao.child} | pai: {relacao.father} | mae: {relacao.mother}")
