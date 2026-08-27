import requests
from bs4 import BeautifulSoup


URL = (
    "https://www.distribuidorasafra.com.br/"
    "fornecedores.php"
)

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    )
}


def main():
    print("Consultando fornecedores públicos da Safra...")

    resposta = requests.get(
        URL,
        headers=CABECALHOS,
        timeout=30,
    )

    print("Status HTTP:", resposta.status_code)
    print(
        "Content-Type:",
        resposta.headers.get("Content-Type"),
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser",
    )

    print("\nTítulos e categorias:\n")

    for elemento in soup.find_all(
        ["h1", "h2", "h3", "h4", "h5", "strong"]
    ):
        texto = elemento.get_text(
            " ",
            strip=True,
        )

        if texto:
            print(
                elemento.name,
                "=>",
                texto,
            )

    print("\nImagens e possíveis fornecedores:\n")

    candidatos = []

    for imagem in soup.find_all("img"):
        alt = imagem.get(
            "alt",
            "",
        ).strip()

        titulo = imagem.get(
            "title",
            "",
        ).strip()

        origem = imagem.get(
            "src",
            "",
        ).strip()

        if alt or titulo:
            candidatos.append({
                "alt": alt,
                "title": titulo,
                "src": origem,
            })

    for numero, candidato in enumerate(
        candidatos,
        start=1,
    ):
        print("-" * 60)
        print("Número:", numero)
        print("ALT:", candidato["alt"])
        print("TITLE:", candidato["title"])
        print("SRC:", candidato["src"])

    print(
        "\nTotal de imagens candidatas:",
        len(candidatos),
    )


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as erro:
        print("Erro de acesso:", erro)

    except Exception as erro:
        print("Erro durante a inspeção:", erro)