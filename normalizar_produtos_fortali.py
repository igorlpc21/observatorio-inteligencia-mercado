import re
import unicodedata
from pathlib import Path

import pandas as pd


arquivo_entrada = (
    Path("dados")
    / "tratados"
    / "produtos_fortali_completo.csv"
)

arquivo_saida = (
    Path("dados")
    / "tratados"
    / "produtos_fortali_normalizados.csv"
)


def normalizar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto)

    # Remove acentos.
    texto = unicodedata.normalize(
        "NFKD",
        texto
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    # Converte para maiúsculas.
    texto = texto.upper()

    # Remove símbolos desnecessários.
    texto = re.sub(
        r"[^A-Z0-9%,. ]",
        " ",
        texto
    )

    # Remove espaços duplicados.
    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def extrair_embalagem(nome_produto):
    if pd.isna(nome_produto):
        return pd.Series({
            "embalagem_original": pd.NA,
            "quantidade": pd.NA,
            "unidade": pd.NA,
            "quantidade_base": pd.NA,
            "unidade_base": pd.NA
        })

    padrao = (
        r"(\d+(?:[.,]\d+)?)"
        r"\s*(KG|ML|G|L)\b"
    )

    resultados = list(
        re.finditer(
            padrao,
            str(nome_produto),
            re.IGNORECASE
        )
    )

    if not resultados:
        return pd.Series({
            "embalagem_original": pd.NA,
            "quantidade": pd.NA,
            "unidade": pd.NA,
            "quantidade_base": pd.NA,
            "unidade_base": pd.NA
        })

    # Utilizamos a última medida encontrada.
    resultado = resultados[-1]

    quantidade = float(
        resultado
        .group(1)
        .replace(",", ".")
    )

    unidade = (
        resultado
        .group(2)
        .upper()
    )

    embalagem_original = (
        resultado
        .group(0)
        .upper()
        .replace(" ", "")
    )

    if unidade == "KG":
        quantidade_base = (
            quantidade * 1000
        )
        unidade_base = "G"

    elif unidade == "G":
        quantidade_base = quantidade
        unidade_base = "G"

    elif unidade == "L":
        quantidade_base = (
            quantidade * 1000
        )
        unidade_base = "ML"

    else:
        quantidade_base = quantidade
        unidade_base = "ML"

    return pd.Series({
        "embalagem_original": (
            embalagem_original
        ),
        "quantidade": quantidade,
        "unidade": unidade,
        "quantidade_base": round(
            quantidade_base,
            2
        ),
        "unidade_base": unidade_base
    })


try:
    df = pd.read_csv(
        arquivo_entrada,
        encoding="utf-8-sig",
        dtype={
            "codigo_produto": "string"
        }
    )

    print(
        f"Registros carregados: {len(df)}"
    )

    df["produto_normalizado"] = (
        df["produto_original"]
        .apply(normalizar_texto)
    )

    dados_embalagem = (
        df["produto_original"]
        .apply(extrair_embalagem)
    )

    df = pd.concat(
        [
            df,
            dados_embalagem
        ],
        axis=1
    )

    df["status_validacao"] = df.apply(
        lambda linha: (
            "Pronto para comparar"
            if (
                pd.notna(
                    linha["codigo_produto"]
                )
                and pd.notna(
                    linha["quantidade_base"]
                )
            )
            else "Revisar embalagem"
        ),
        axis=1
    )

    colunas_saida = [
        "empresa",
        "departamento",
        "produto_original",
        "produto_normalizado",
        "codigo_produto",
        "embalagem_original",
        "quantidade",
        "unidade",
        "quantidade_base",
        "unidade_base",
        "preco",
        "preco_publico",
        "pagina_catalogo",
        "link_produto",
        "data_coleta",
        "fonte",
        "status_validacao"
    ]

    colunas_existentes = [
        coluna
        for coluna in colunas_saida
        if coluna in df.columns
    ]

    df = df[colunas_existentes]

    df.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nNormalização concluída!")
    print(
        f"Arquivo salvo em: "
        f"{arquivo_saida}"
    )

    print("\nResumo da validação:")

    print(
        df["status_validacao"]
        .value_counts()
        .to_string()
    )

    print("\nPrimeiros produtos:")

    print(
        df[
            [
                "produto_original",
                "embalagem_original",
                "quantidade_base",
                "unidade_base",
                "status_validacao"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


except FileNotFoundError:
    print(
        f"Arquivo não encontrado: "
        f"{arquivo_entrada}"
    )

except Exception as erro:
    print(
        f"Erro durante a normalização: "
        f"{erro}"
    )