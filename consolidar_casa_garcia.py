import re
import unicodedata
from pathlib import Path

import pandas as pd


ARQUIVO_MESTRE = (
    Path("dados")
    / "tratados"
    / "catalogo_mestre_inicial.csv"
)

ARQUIVO_CASA_GARCIA = (
    Path("dados")
    / "tratados"
    / "produtos_casa_garcia_normalizados.csv"
)

ARQUIVO_SAIDA = (
    Path("dados")
    / "tratados"
    / "catalogo_mestre_3_empresas.csv"
)


def normalizar_identificador(texto):
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
        "_",
        texto,
    )

    return texto.strip("_").upper()


def main():
    mestre = pd.read_csv(
        ARQUIVO_MESTRE,
        dtype={
            "codigo_produto": "string",
            "id_registro": "string",
        },
    )

    casa = pd.read_csv(
        ARQUIVO_CASA_GARCIA,
        dtype={
            "codigo_produto": "string",
        },
    )

    casa = casa.rename(
        columns={
            "data_coleta": "data_referencia",
        }
    )

    casa["codigo_valido"] = (
    casa["codigo_produto"]
        .fillna("")
        .str.strip()
        .ne("")
    )

    casa["id_registro"] = casa.apply(
        lambda linha: (
            "CG_"
            + normalizar_identificador(
                linha["departamento"]
            )
            + "_"
            + normalizar_identificador(
                linha["codigo_produto"]
            )
        ),
        axis=1,
    )

    casa["metodo_extracao"] = (
        "Web scraping de catálogo público"
    )

    casa["qualidade_extracao"] = casa[
        "status_validacao"
    ].map({
        "VALIDO": "ALTA",
        "REVISAR_EMBALAGEM": "MEDIA",
        "REVISAR_NOME": "BAIXA",
        "REVISAR_CODIGO": "BAIXA",
    }).fillna("MEDIA")

    # Garante todas as colunas do catálogo mestre.
    for coluna in mestre.columns:
        if coluna not in casa.columns:
            casa[coluna] = pd.NA

    # Mantém exatamente a mesma ordem do catálogo mestre.
    casa = casa[mestre.columns]

    catalogo = pd.concat(
        [
            mestre,
            casa,
        ],
        ignore_index=True,
    )

    duplicados_id = catalogo[
        "id_registro"
    ].duplicated().sum()

    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    catalogo.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print("Consolidação concluída!")
    print("Registros anteriores:", len(mestre))
    print("Casa Garcia adicionados:", len(casa))
    print("Total consolidado:", len(catalogo))
    print("IDs duplicados:", duplicados_id)
    print("Arquivo:", ARQUIVO_SAIDA)

    print("\nRegistros por empresa:")
    print(
        catalogo[
            "empresa"
        ].value_counts(
            dropna=False
        )
    )


if __name__ == "__main__":
    main()