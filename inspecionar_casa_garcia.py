import re

import requests
from bs4 import BeautifulSoup


URL = (
    "https://casagarciafortaleza.com.br/"
    "index.php?cat=confeitaria"
    "&idcat=1"
    "&name=Confeitaria"
    "&topicos=nav%2Fcategoria_single"
)

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    )
}

PADRAO_EMBALAGEM = re.compile(
    r"\b\d+(?:[.,]\d+)?\s*"
    r"(?:KG|G|L|ML|UN|UND|CM)\b",
    flags=re.IGNORECASE,
)


def main():
    print("Consultando página pública da Casa Garcia...")

    resposta = requests.get(
        URL,
        headers=CABECALHOS,
        timeout=30,
    )

    print(f"Status HTTP: {resposta.status_code}")
    print(f"Content-Type: {resposta.headers.get('Content-Type')}")

    if resposta.status_code != 200:
        print("A página não pôde ser analisada.")
        return

    soup = BeautifulSoup(
        resposta.text,
        "html.parser",
    )

    titulo = (
        soup.title.get_text(strip=True)
        if soup.title
        else "Título não encontrado"
    )

    print(f"Título: {titulo}")

    candidatos = []
    textos_vistos = set()

    elementos = soup.find_all(
        [
            "a",
            "div",
            "span",
            "p",
            "h2",
            "h3",
            "h4",
            "li",
        ]
    )

    for elemento in elementos:
        texto = elemento.get_text(
            " ",
            strip=True,
        )

        if not texto:
            continue

        if len(texto) > 180:
            continue

        if texto in textos_vistos:
            continue

        if not PADRAO_EMBALAGEM.search(texto):
            continue

        textos_vistos.add(texto)

        candidatos.append({
            "tag": elemento.name,
            "classe": elemento.get("class", []),
            "texto": texto,
        })

    print(
        "\nCandidatos a produtos encontrados:",
        len(candidatos),
    )

    print("\nPrimeiros candidatos:\n")

    for numero, candidato in enumerate(
        candidatos[:80],
        start=1,
    ):
        print("-" * 60)
        print(f"Número: {numero}")
        print(f"Tag: {candidato['tag']}")
        print(f"Classe: {candidato['classe']}")
        print(f"Texto: {candidato['texto']}")

    print("\nInspeção concluída!")


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as erro:
        print(f"Erro de acesso: {erro}")

    except Exception as erro:
        print(f"Erro durante a inspeção: {erro}")