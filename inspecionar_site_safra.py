from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


url = "https://mercadodosabor.com.br/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}


try:
    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(
        f"Status HTTP: "
        f"{resposta.status_code}"
    )

    print(
        f"Endereço final: "
        f"{resposta.url}"
    )

    resposta.raise_for_status()

    pasta_brutos = (
        Path("dados")
        / "brutos"
    )

    pasta_brutos.mkdir(
        parents=True,
        exist_ok=True
    )

    caminho_html = (
        pasta_brutos
        / "mercado_sabor_home.html"
    )

    caminho_html.write_text(
        resposta.text,
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    titulo = (
        soup.title.get_text(
            strip=True
        )
        if soup.title
        else "Título não encontrado"
    )

    scripts = []

    for elemento in soup.find_all(
        "script",
        src=True
    ):
        endereco = urljoin(
            resposta.url,
            elemento["src"]
        )

        scripts.append(endereco)

    links = []

    for elemento in soup.find_all(
        "a",
        href=True
    ):
        endereco = urljoin(
            resposta.url,
            elemento["href"]
        )

        if endereco not in links:
            links.append(endereco)

    print(f"Título: {titulo}")

    print(
        f"Scripts encontrados: "
        f"{len(scripts)}"
    )

    for numero, script in enumerate(
        scripts[:20],
        start=1
    ):
        print(
            f"{numero}. {script}"
        )

    print(
        f"\nLinks encontrados: "
        f"{len(links)}"
    )

    for numero, link in enumerate(
        links[:20],
        start=1
    ):
        print(
            f"{numero}. {link}"
        )

    print(
        f"\nHTML salvo em: "
        f"{caminho_html}"
    )


except requests.RequestException as erro:
    print(
        f"Erro de acesso: {erro}"
    )

except Exception as erro:
    print(
        f"Erro durante a inspeção: "
        f"{erro}"
    )