import json
from pathlib import Path

import requests


url = (
    "https://merconnect.mercadapp.com.br"
    "/mapp/v2/markets"
)

parametros = {
    "brand_id": 875
}

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "pt-BR,pt;q=0.9"
}


try:
    resposta = requests.get(
        url,
        params=parametros,
        headers=headers,
        timeout=30
    )

    print(
        f"Status HTTP: "
        f"{resposta.status_code}"
    )

    print(
        f"Endereço consultado: "
        f"{resposta.url}"
    )

    print(
        f"Tipo de conteúdo: "
        f"{resposta.headers.get('content-type')}"
    )

    if resposta.status_code == 200:
        dados = resposta.json()

        caminho_saida = (
            Path("dados")
            / "brutos"
            / "lojas_mercado_sabor.json"
        )

        caminho_saida.write_text(
            json.dumps(
                dados,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        print(
            f"\nJSON salvo em: "
            f"{caminho_saida}"
        )

        if isinstance(dados, dict):
            print(
                "\nChaves principais:"
            )

            for chave in dados.keys():
                print(f"- {chave}")

            lojas = (
                dados.get("markets")
                or dados.get("data")
                or []
            )

        elif isinstance(dados, list):
            lojas = dados

        else:
            lojas = []

        print(
            f"\nQuantidade de lojas: "
            f"{len(lojas)}"
        )

        for numero, loja in enumerate(
            lojas[:10],
            start=1
        ):
            print(
                f"\n--- LOJA {numero} ---"
            )

            print(
                f"ID: {loja.get('id')}"
            )

            print(
                "Nome:",
                loja.get("name")
                or loja.get("display_name")
                or loja.get("description")
            )

            print(
                "Cidade:",
                loja.get("city")
            )

            print(
                "Bairro:",
                loja.get("neighborhood")
            )

    else:
        print(
            "\nA rota não está disponível "
            "anonimamente."
        )

        print(
            "Resposta recebida:"
        )

        print(
            resposta.text[:500]
        )

        print(
            "\nNão utilizaremos tokens "
            "encontrados no JavaScript."
        )


except requests.RequestException as erro:
    print(
        f"Erro de acesso: {erro}"
    )

except ValueError:
    print(
        "A resposta não está em JSON."
    )

except Exception as erro:
    print(
        f"Erro durante o teste: {erro}"
    )