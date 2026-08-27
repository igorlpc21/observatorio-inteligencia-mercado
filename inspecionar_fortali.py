import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup


url = "https://www.fortali.com.br/confeitaria"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}


try:
    resposta = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print(f"Status HTTP: {resposta.status_code}")

    resposta.raise_for_status()

    pasta_brutos = Path("dados") / "brutos"
    pasta_brutos.mkdir(parents=True, exist_ok=True)

    caminho_html = pasta_brutos / "fortali_confeitaria.html"

    caminho_html.write_text(
        resposta.text,
        encoding="utf-8"
    )

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    titulo = (
        soup.title.get_text(strip=True)
        if soup.title
        else "Título não encontrado"
    )

    textos_codigo = soup.find_all(
        string=lambda texto: (
            texto
            and re.search(
                r"Código\s*:",
                texto,
                re.IGNORECASE
            )
        )
    )

    print(f"Título da página: {titulo}")
    print(f"Referências a códigos: {len(textos_codigo)}")
    print(f"HTML salvo em: {caminho_html}")

    print("\nPrimeiros blocos encontrados:")

    for numero, texto_codigo in enumerate(
        textos_codigo[:10],
        start=1
    ):
        bloco = texto_codigo.parent

        for _ in range(4):
            conteudo = bloco.get_text(
                " ",
                strip=True
            )

            if 30 <= len(conteudo) <= 700:
                break

            if bloco.parent is None:
                break

            bloco = bloco.parent

        conteudo = bloco.get_text(
            " ",
            strip=True
        )

        print(f"\n--- BLOCO {numero} ---")
        print(f"Tag: {bloco.name}")
        print(f"Classe: {bloco.get('class')}")
        print(conteudo[:500])


except requests.RequestException as erro:
    print(f"Erro de acesso ao site: {erro}")

except Exception as erro:
    print(f"Erro durante o tratamento: {erro}")