import re
import unicodedata
from pathlib import Path

import pandas as pd


ARQUIVO_ENTRADA = (
    Path("dados")
    / "brutos"
    / "produtos_casa_garcia_completo.csv"
)

ARQUIVO_SAIDA = (
    Path("dados")
    / "tratados"
    / "produtos_casa_garcia_normalizados.csv"
)

PADRAO_MEDIDA = re.compile(
    r"(?<!\d)(\d+(?:[.,]\d+)?)\s*"
    r"(KG|G|L|ML|UN|UND|CM)\b",
    flags=re.IGNORECASE,
)


def remover_acentos(texto):
    texto = str(texto)

    return "".join(
        caractere
        for caractere in unicodedata.normalize("NFD", texto)
        if unicodedata.category(caractere) != "Mn"
    )


def normalizar_texto(texto):
    if pd.isna(texto):
        return ""

    texto = remover_acentos(texto).upper()

    # Remove peso ou volume do nome normalizado,
    # pois será armazenado em colunas próprias.
    texto = PADRAO_MEDIDA.sub(" ", texto)

    texto = re.sub(
        r"[^A-Z0-9]+",
        " ",
        texto,
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip()


def extrair_medida(nome_produto):
    if pd.isna(nome_produto):
        return pd.NA, pd.NA

    resultados = PADRAO_MEDIDA.findall(
        str(nome_produto)
    )

    if not resultados:
        return pd.NA, pd.NA

    quantidade_texto, unidade = resultados[-1]

    quantidade = float(
        quantidade_texto.replace(",", ".")
    )

    unidade = unidade.upper()

    if unidade == "UND":
        unidade = "UN"

    return quantidade, unidade


def converter_para_base(quantidade, unidade):
    if pd.isna(quantidade) or pd.isna(unidade):
        return pd.NA, pd.NA

    if unidade == "KG":
        return quantidade * 1000, "G"

    if unidade == "G":
        return quantidade, "G"

    if unidade == "L":
        return quantidade * 1000, "ML"

    if unidade == "ML":
        return quantidade, "ML"

    if unidade == "UN":
        return quantidade, "UN"

    if unidade == "CM":
        return quantidade, "CM"

    return quantidade, unidade


def definir_status(linha):
    if not linha["produto_original"]:
        return "REVISAR_NOME"

    if not linha["codigo_produto"]:
        return "REVISAR_CODIGO"

    if pd.isna(linha["quantidade"]):
        return "REVISAR_EMBALAGEM"

    return "VALIDO"


def main():
    if not ARQUIVO_ENTRADA.exists():
        print(
            "Arquivo não encontrado:",
            ARQUIVO_ENTRADA,
        )
        return

    dados = pd.read_csv(
        ARQUIVO_ENTRADA,
        dtype={
            "codigo_produto": "string",
        },
    )

    dados["produto_original"] = (
        dados["produto_original"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    dados["codigo_produto"] = (
        dados["codigo_produto"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.replace(
            r"\.0$",
            "",
            regex=True,
        )
    )

    dados["produto_normalizado"] = (
        dados["produto_original"]
        .apply(normalizar_texto)
    )

    medidas = (
        dados["produto_original"]
        .apply(extrair_medida)
    )

    dados["quantidade"] = [
        medida[0]
        for medida in medidas
    ]

    dados["unidade"] = [
        medida[1]
        for medida in medidas
    ]

    medidas_base = [
        converter_para_base(
            quantidade,
            unidade,
        )
        for quantidade, unidade in zip(
            dados["quantidade"],
            dados["unidade"],
        )
    ]

    dados["quantidade_base"] = [
        medida[0]
        for medida in medidas_base
    ]

    dados["unidade_base"] = [
        medida[1]
        for medida in medidas_base
    ]

    resultado = pd.DataFrame({
        "empresa": "Casa Garcia Gourmet",
        "departamento": dados["categoria"],
        "produto_original": dados["produto_original"],
        "produto_normalizado": dados["produto_normalizado"],
        "codigo_produto": dados["codigo_produto"],
        "embalagem_original": dados["embalagem_caixa"],
        "quantidade": dados["quantidade"],
        "unidade": dados["unidade"],
        "quantidade_base": dados["quantidade_base"],
        "unidade_base": dados["unidade_base"],
        "preco": pd.NA,
        "preco_publico": False,
        "pagina_catalogo": dados["pagina_catalogo"],
        "link_produto": pd.NA,
        "data_coleta": dados["data_coleta"],
        "fonte": dados["fonte"],
    })

    resultado["status_validacao"] = (
        resultado.apply(
            definir_status,
            axis=1,
        )
    )

    resultado = resultado.drop_duplicates(
        subset=[
            "departamento",
            "codigo_produto",
        ]
    )

    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    resultado.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print("Tratamento concluído!")
    print("Registros:", len(resultado))
    print("Arquivo:", ARQUIVO_SAIDA)

    print("\nStatus de validação:")
    print(
        resultado[
            "status_validacao"
        ].value_counts(
            dropna=False
        )
    )

    print("\nProdutos por departamento:")
    print(
        resultado[
            "departamento"
        ].value_counts()
    )


if __name__ == "__main__":
    main()