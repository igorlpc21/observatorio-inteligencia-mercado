import requests
from bs4 import BeautifulSoup


url = "https://www.fortali.com.br/confeitaria"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}


try:
    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(f"Status HTTP: {resposta.status_code}")

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    elementos_encontrados = []

    for elemento in soup.find_all(
        ["a", "button"]
    ):
        texto = elemento.get_text(
            " ",
            strip=True
        ).lower()

        atributos = str(
            elemento.attrs
        ).lower()

        if (
            "próxima" in texto
            or "proxima" in texto
            or "next" in texto
            or "próxima" in atributos
            or "proxima" in atributos
            or "next" in atributos
        ):
            elementos_encontrados.append(
                elemento
            )

    print(
        "\nElementos de paginação encontrados:",
        len(elementos_encontrados)
    )

    for numero, elemento in enumerate(
        elementos_encontrados,
        start=1
    ):
        print(f"\n--- ELEMENTO {numero} ---")
        print(f"Tag: {elemento.name}")
        print(f"Texto: {elemento.get_text(' ', strip=True)}")
        print(f"Atributos: {elemento.attrs}")
        print("HTML:")
        print(str(elemento)[:1500])


except requests.RequestException as erro:
    print(f"Erro de acesso: {erro}")

except Exception as erro:
    print(f"Erro durante a inspeção: {erro}")