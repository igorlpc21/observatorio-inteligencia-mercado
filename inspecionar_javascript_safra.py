import re
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


url_site = "https://mercadodosabor.com.br/"

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9"
}

palavras_importantes = [
    "api",
    "produto",
    "catalogo",
    "graphql",
    "baseurl",
    "categoria"
]


try:
    resposta = requests.get(
        url_site,
        headers=headers,
        timeout=30
    )

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    pasta_saida = (
        Path("dados")
        / "brutos"
        / "javascript_safra"
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True
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

        if "mercadodosabor.com.br" in endereco:
            scripts.append(endereco)

    print(
        f"Scripts do site encontrados: "
        f"{len(scripts)}"
    )

    resultados = set()

    for numero, endereco_script in enumerate(
        scripts,
        start=1
    ):
        print(
            f"\nBaixando script {numero}: "
            f"{endereco_script}"
        )

        resposta_script = requests.get(
            endereco_script,
            headers=headers,
            timeout=60
        )

        print(
            f"Status: "
            f"{resposta_script.status_code}"
        )

        resposta_script.raise_for_status()

        conteudo = resposta_script.text

        nome_arquivo = (
            endereco_script
            .split("/")[-1]
        )

        caminho_script = (
            pasta_saida
            / nome_arquivo
        )

        caminho_script.write_text(
            conteudo,
            encoding="utf-8"
        )

        # Corrige barras escapadas comuns
        # em arquivos JavaScript.
        conteudo_limpo = (
            conteudo
            .replace("\\/", "/")
        )

        urls = re.findall(
            r"https?://[^\"'\s\\]+",
            conteudo_limpo
        )

        for endereco in urls:
            endereco_minusculo = (
                endereco.lower()
            )

            if any(
                palavra in endereco_minusculo
                for palavra
                in palavras_importantes
            ):
                resultados.add(
                    endereco[:500]
                )

        conteudo_minusculo = (
            conteudo_limpo.lower()
        )

        for palavra in palavras_importantes:
            inicio_busca = 0
            ocorrencias = 0

            while ocorrencias < 3:
                posicao = (
                    conteudo_minusculo.find(
                        palavra,
                        inicio_busca
                    )
                )

                if posicao == -1:
                    break

                inicio = max(
                    0,
                    posicao - 150
                )

                fim = min(
                    len(conteudo_limpo),
                    posicao + 350
                )

                trecho = (
                    conteudo_limpo[
                        inicio:fim
                    ]
                    .replace("\n", " ")
                )

                resultados.add(
                    trecho
                )

                inicio_busca = (
                    posicao
                    + len(palavra)
                )

                ocorrencias += 1

    print(
        "\n=== ENDEREÇOS E TRECHOS "
        "IMPORTANTES ==="
    )

    resultados_ordenados = sorted(
        resultados
    )

    print(
        f"Resultados encontrados: "
        f"{len(resultados_ordenados)}"
    )

    for numero, resultado in enumerate(
        resultados_ordenados[:40],
        start=1
    ):
        print(
            f"\n--- RESULTADO {numero} ---"
        )
        print(resultado)

    print(
        f"\nScripts salvos em: "
        f"{pasta_saida}"
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