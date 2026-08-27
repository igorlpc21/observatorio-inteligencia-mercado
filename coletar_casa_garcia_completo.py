import re
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup, NavigableString


URL_BASE = (
    "https://casagarciafortaleza.com.br/index.php"
)

CATEGORIA = "Confeitaria"
MAXIMO_PAGINAS = 100

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    )
}

PADRAO_CODIGO = re.compile(
    r"^Confeitaria\s*-\s*(\d+)$",
    flags=re.IGNORECASE,
)

PADRAO_CAIXA = re.compile(
    r"^(CX|FD|SC|PC|UN|DS)\s*\d+$",
    flags=re.IGNORECASE,
)


def obter_textos_seguintes(titulo):
    textos = []

    for elemento in titulo.next_elements:
        if not isinstance(
            elemento,
            NavigableString,
        ):
            continue

        texto = " ".join(
            str(elemento).split()
        )

        if not texto:
            continue

        if texto == titulo.get_text(
            " ",
            strip=True,
        ):
            continue

        textos.append(texto)

        if len(textos) >= 20:
            break

    return textos


def extrair_produtos(soup, pagina):
    produtos = []

    for titulo in soup.find_all("h6"):
        nome = titulo.get_text(
            " ",
            strip=True,
        )

        if not nome:
            continue

        textos = obter_textos_seguintes(
            titulo
        )

        codigo = None
        marca = ""
        embalagem_caixa = ""

        for indice, texto in enumerate(textos):
            resultado = PADRAO_CODIGO.match(
                texto
            )

            if not resultado:
                continue

            codigo = resultado.group(1)

            if indice > 0:
                marca = textos[indice - 1]

            for texto_posterior in textos[
                indice + 1:
            ]:
                if PADRAO_CAIXA.match(
                    texto_posterior
                ):
                    embalagem_caixa = (
                        texto_posterior
                    )
                    break

            break

        if codigo is None:
            continue

        produtos.append({
            "empresa": "Casa Garcia Gourmet",
            "categoria": CATEGORIA,
            "produto_original": nome,
            "marca": marca,
            "codigo_produto": codigo,
            "embalagem_caixa": embalagem_caixa,
            "pagina_catalogo": pagina,
            "data_coleta": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "fonte": URL_BASE,
        })

    return produtos


def main():
    global CATEGORIA
    global PADRAO_CODIGO

    categorias = [
        {
            "nome": "Confeitaria",
            "cat": "confeitaria",
            "idcat": 1,
        },
        {
            "nome": "Panificação",
            "cat": "Panificação",
            "idcat": 2,
        },
        {
            "nome": "Food Service",
            "cat": "Food Service",
            "idcat": 3,
        },
        {
            "nome": "Acessórios",
            "cat": "Acessórios",
            "idcat": 4,
        },
        {
            "nome": "Equipamentos",
            "cat": "Equipamentos",
            "idcat": 5,
        },
    ]

    todos_produtos = []

    sessao = requests.Session()
    sessao.headers.update(CABECALHOS)

    for configuracao in categorias:
        CATEGORIA = configuracao["nome"]

        PADRAO_CODIGO = re.compile(
            rf"^{re.escape(CATEGORIA)}\s*-\s*(\d+)$",
            flags=re.IGNORECASE,
        )

        codigos_coletados = set()

        print("\n" + "=" * 60)
        print(f"Coletando categoria: {CATEGORIA}")
        print("=" * 60)

        for pagina in range(
            1,
            MAXIMO_PAGINAS + 1,
        ):
            parametros = {
                "cat": configuracao["cat"],
                "idcat": configuracao["idcat"],
                "name": CATEGORIA,
                "pagina": pagina,
                "topicos": "nav/categoria_single",
            }

            try:
                resposta = sessao.get(
                    URL_BASE,
                    params=parametros,
                    timeout=30,
                )

                print(
                    f"Página {pagina} | "
                    f"Status: {resposta.status_code}"
                )

                resposta.raise_for_status()

            except requests.RequestException as erro:
                print(f"Erro de acesso: {erro}")
                break

            soup = BeautifulSoup(
                resposta.text,
                "html.parser",
            )

            produtos_pagina = extrair_produtos(
                soup,
                pagina,
            )

            novos_produtos = []

            for produto in produtos_pagina:
                codigo = produto["codigo_produto"]

                if codigo in codigos_coletados:
                    continue

                codigos_coletados.add(codigo)
                novos_produtos.append(produto)

            if not novos_produtos:
                print(
                    "Nenhum produto novo encontrado. "
                    "Categoria encerrada."
                )
                break

            todos_produtos.extend(novos_produtos)

            print(
                f"Produtos novos: "
                f"{len(novos_produtos)}"
            )

            time.sleep(1)

        print(
            f"Total em {CATEGORIA}: "
            f"{len(codigos_coletados)}"
        )

    if not todos_produtos:
        print("Nenhum produto foi coletado.")
        return

    df_produtos = pd.DataFrame(todos_produtos)

    df_produtos = df_produtos.drop_duplicates(
        subset=[
            "categoria",
            "codigo_produto",
        ]
    )

    pasta_saida = (
        Path("dados")
        / "brutos"
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_saida = (
        pasta_saida
        / "produtos_casa_garcia_completo.csv"
    )

    df_produtos.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nColeta completa concluída!")
    print(f"Produtos coletados: {len(df_produtos)}")
    print(f"Arquivo salvo em: {arquivo_saida}")

    print("\nProdutos por categoria:")
    print(
        df_produtos[
            "categoria"
        ].value_counts()
    )


if __name__ == "__main__":
    main()