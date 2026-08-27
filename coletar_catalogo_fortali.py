import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup


URL_BASE = "https://www.fortali.com.br/confeitaria"

# Inicialmente, vamos testar somente 3 páginas.
LIMITE_PAGINAS = 150

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


produtos = []
codigos_coletados = set()

pagina = 1
data_coleta = datetime.now().strftime(
    "%Y-%m-%d %H:%M:%S"
)


try:
    while pagina <= LIMITE_PAGINAS:
        url_pagina = (
            f"{URL_BASE}?page={pagina}"
        )

        print(
            f"\nColetando página {pagina}: "
            f"{url_pagina}"
        )

        resposta = requests.get(
            url_pagina,
            headers=headers,
            timeout=30
        )

        print(
            f"Status HTTP: "
            f"{resposta.status_code}"
        )

        resposta.raise_for_status()

        soup = BeautifulSoup(
            resposta.text,
            "html.parser"
        )

        cards = soup.select(
            "div.product-card__info"
        )

        print(
            f"Cards encontrados: "
            f"{len(cards)}"
        )

        if not cards:
            print(
                "Nenhum produto encontrado. "
                "Coleta encerrada."
            )
            break

        produtos_novos = 0

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

            if not resultado:
                continue

            nome_produto = (
                resultado.group(1).strip()
            )

            codigo_produto = (
                resultado.group(2).strip()
            )

            if codigo_produto in codigos_coletados:
                continue

            link_elemento = card.find(
                "a",
                href=True
            )

            if link_elemento:
                link_produto = urljoin(
                    URL_BASE,
                    link_elemento["href"]
                )
            else:
                link_produto = pd.NA

            codigos_coletados.add(
                codigo_produto
            )

            produtos.append({
                "empresa": "Fortali Distribuidora",
                "departamento": "Confeitaria",
                "produto_original": nome_produto,
                "codigo_produto": codigo_produto,
                "preco": pd.NA,
                "preco_publico": "Não",
                "pagina_catalogo": pagina,
                "link_produto": link_produto,
                "data_coleta": data_coleta,
                "fonte": url_pagina
            })

            produtos_novos += 1

        print(
            f"Produtos novos: "
            f"{produtos_novos}"
        )

        if produtos_novos == 0:
            print(
                "A página não trouxe produtos novos. "
                "Coleta encerrada."
            )
            break

        pagina += 1

        # Pequena pausa para não sobrecarregar o site.
        time.sleep(1)


    df_produtos = pd.DataFrame(
        produtos
    )

    if not df_produtos.empty:
        df_produtos = (
            df_produtos
            .drop_duplicates(
                subset=[
                    "empresa",
                    "codigo_produto"
                ]
            )
            .sort_values(
                by="codigo_produto"
            )
        )

        pasta_saida = (
            Path("dados")
            / "tratados"
        )

        pasta_saida.mkdir(
            parents=True,
            exist_ok=True
        )

        caminho_saida = (
            pasta_saida
            / "produtos_fortali_teste.csv"
        )

        df_produtos.to_csv(
            caminho_saida,
            index=False,
            encoding="utf-8-sig"
        )

        print("\nColeta concluída!")
        print(
            f"Total de produtos: "
            f"{len(df_produtos)}"
        )
        print(
            f"Páginas coletadas: "
            f"{df_produtos['pagina_catalogo'].nunique()}"
        )
        print(
            f"Arquivo salvo em: "
            f"{caminho_saida}"
        )

        print("\nProdutos por página:")

        print(
            df_produtos[
                "pagina_catalogo"
            ]
            .value_counts()
            .sort_index()
            .to_string()
        )

    else:
        print(
            "Nenhum produto foi coletado."
        )


except requests.RequestException as erro:
    print(f"Erro de acesso ao site: {erro}")

except Exception as erro:
    print(f"Erro durante a coleta: {erro}")