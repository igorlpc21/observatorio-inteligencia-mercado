import requests
from bs4 import BeautifulSoup

url = "https://milkdistribuidora.com.br/"

cabecalhos = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1"
}

try:
    resposta = requests.get(
        url,
        headers=cabecalhos,
        timeout=20
    )

    print(f"Status HTTP: {resposta.status_code}")

    if resposta.status_code == 200:
        pagina = BeautifulSoup(
            resposta.text,
            "html.parser"
        )

        if pagina.title:
            titulo = pagina.title.get_text(strip=True)
        else:
            titulo = "Título não encontrado"

        links = pagina.find_all("a", href=True)

        elementos_titulo = pagina.find_all(
            ["h1", "h2", "h3", "h4"]
        )

        titulos_encontrados = []

        for elemento in elementos_titulo:
            texto = elemento.get_text(
                " ",
                strip=True
            )

            if texto and texto not in titulos_encontrados:
                titulos_encontrados.append(texto)

        print(f"Título da página: {titulo}")
        print(f"Quantidade de links: {len(links)}")
        print(
            "Quantidade de títulos encontrados: "
            f"{len(titulos_encontrados)}"
        )

        print("\nTítulos encontrados na página:")

        for numero, texto in enumerate(
            titulos_encontrados,
            start=1
        ):
            print(f"{numero}. {texto}")

    else:
        print(
            "O site respondeu, mas a página "
            "não foi carregada corretamente."
        )

except requests.RequestException as erro:
    print(f"Erro durante a coleta: {erro}")