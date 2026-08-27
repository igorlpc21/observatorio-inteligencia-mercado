import re
from datetime import datetime
from pathlib import Path

import pandas as pd
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

    soup = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    cards = soup.select(
        "div.product-card__info"
    )

    print(f"Cards encontrados: {len(cards)}")

    produtos = []

    for card in cards:
        texto = card.get_text(
            " ",
            strip=True
        )

        resultado = re.search(
            r"^(.*?)\s+C[oó]digo\s*:\s*(\d+)",
            texto,
            re.IGNORECASE
        )

        if resultado:
            nome_produto = resultado.group(1).strip()
            codigo_produto = resultado.group(2).strip()

            produtos.append({
                "empresa": "Fortali Distribuidora",
                "departamento": "Confeitaria",
                "produto_original": nome_produto,
                "codigo_produto": codigo_produto,
                "preco": pd.NA,
                "preco_publico": "Não",
                "data_coleta": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "fonte": url
            })

    df_produtos = pd.DataFrame(produtos)

    if not df_produtos.empty:
        df_produtos = df_produtos.drop_duplicates(
            subset=[
                "empresa",
                "codigo_produto"
            ]
        )

        pasta_saida = Path("dados") / "tratados"

        pasta_saida.mkdir(
            parents=True,
            exist_ok=True
        )

        caminho_saida = (
            pasta_saida
            / "produtos_fortali_pagina1.csv"
        )

        df_produtos.to_csv(
            caminho_saida,
            index=False,
            encoding="utf-8-sig"
        )

        print("\nExtração concluída!")
        print(
            f"Produtos extraídos: "
            f"{len(df_produtos)}"
        )
        print(
            f"Arquivo salvo em: "
            f"{caminho_saida}"
        )

        print("\nPrimeiros produtos:")

        print(
            df_produtos[
                [
                    "produto_original",
                    "codigo_produto"
                ]
            ]
            .head(10)
            .to_string(index=False)
        )

    else:
        print(
            "Nenhum produto foi reconhecido."
        )


except requests.RequestException as erro:
    print(f"Erro de acesso ao site: {erro}")

except Exception as erro:
    print(f"Erro durante o tratamento: {erro}")