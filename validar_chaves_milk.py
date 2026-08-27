import hashlib
import re
import unicodedata
from pathlib import Path

import pandas as pd


ENTRADA = (
    Path("dados")
    / "tratados"
    / "produtos_milk_normalizados_iniciais.csv"
)

SAIDA = (
    Path("dados")
    / "tratados"
    / "produtos_milk_validados.csv"
)

CODIGOS_PLACEHOLDER = {
    "",
    "X",
    "XX",
    "XXX",
    "N/A",
    "NA",
    "NULL",
    "NONE",
}


def normalizar_texto(texto):
    texto = unicodedata.normalize(
        "NFD",
        str(texto),
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(
        r"[^A-Za-z0-9]+",
        " ",
        texto,
    )

    return re.sub(
        r"\s+",
        " ",
        texto,
    ).strip().upper()


def gerar_id(linha):
    if linha["codigo_valido"]:
        codigo = normalizar_texto(
            linha["codigo_produto"]
        ).replace(" ", "_")

        return f"MILK_COD_{codigo}"

    nome = normalizar_texto(
        linha["produto_extraido"]
    )

    assinatura = hashlib.sha256(
        nome.encode("utf-8")
    ).hexdigest()[:16].upper()

    return f"MILK_NOME_{assinatura}"


def main():
    dados = pd.read_csv(
        ENTRADA,
        dtype="string",
    )

    dados["codigo_produto_original"] = (
        dados["codigo_produto"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    codigo_normalizado = (
        dados["codigo_produto_original"]
    )

    placeholder = codigo_normalizado.isin(
        CODIGOS_PLACEHOLDER
    )

    candidatos_validos = dados[
        ~placeholder
    ].copy()

    conflitos = (
        candidatos_validos
        .groupby("codigo_produto_original")[
            "produto_extraido"
        ]
        .nunique()
    )

    codigos_conflitantes = set(
        conflitos[
            conflitos > 1
        ].index
    )

    conflito = codigo_normalizado.isin(
        codigos_conflitantes
    )

    dados["codigo_valido"] = (
        ~placeholder
        & ~conflito
    )

    dados["motivo_codigo"] = "CODIGO_VALIDO"

    dados.loc[
        placeholder,
        "motivo_codigo",
    ] = "CODIGO_PLACEHOLDER"

    dados.loc[
        conflito,
        "motivo_codigo",
    ] = "CODIGO_CONFLITANTE"

    # Remove o código inválido da chave analítica,
    # preservando-o em codigo_produto_original.
    dados.loc[
        ~dados["codigo_valido"],
        "codigo_produto",
    ] = pd.NA

    dados["id_registro"] = dados.apply(
        gerar_id,
        axis=1,
    )

    dados["status_validacao"] = (
        dados["codigo_valido"]
        .map({
            True: "VALIDO",
            False: "REVISAR_CODIGO",
        })
    )

    duplicados_id = int(
        dados["id_registro"]
        .duplicated()
        .sum()
    )

    dados.to_csv(
        SAIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print("Validação concluída!")
    print("Registros preservados:", len(dados))
    print(
        "Códigos válidos:",
        int(dados["codigo_valido"].sum()),
    )
    print(
        "Códigos placeholder:",
        int(placeholder.sum()),
    )
    print(
        "Códigos conflitantes:",
        int(conflito.sum()),
    )
    print(
        "IDs técnicos duplicados:",
        duplicados_id,
    )
    print("Arquivo:", SAIDA)

    print("\nMotivos:")
    print(
        dados[
            "motivo_codigo"
        ].value_counts()
    )


if __name__ == "__main__":
    main()