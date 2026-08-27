from pathlib import Path

import pandas as pd


PASTA = Path("dados") / "tratados"

CATALOGO_ATUAL = (
    PASTA
    / "catalogo_mestre_3_empresas.csv"
)

MILK_VALIDADA = (
    PASTA
    / "produtos_milk_validados.csv"
)

ARQUIVO_SAIDA = (
    PASTA
    / "catalogo_mestre_validado.csv"
)


def montar_embalagem(linha):
    quantidade = linha.get(
        "quantidade_original"
    )

    unidade = linha.get(
        "unidade_original"
    )

    if pd.isna(quantidade):
        return pd.NA

    quantidade = str(quantidade).strip()

    if not quantidade:
        return pd.NA

    if pd.isna(unidade):
        return quantidade

    unidade = str(unidade).strip()

    return f"{quantidade} {unidade}".strip()


def main():
    catalogo = pd.read_csv(
        CATALOGO_ATUAL,
        dtype={
            "id_registro": "string",
            "codigo_produto": "string",
        },
    )

    milk = pd.read_csv(
        MILK_VALIDADA,
        dtype={
            "id_registro": "string",
            "codigo_produto": "string",
        },
    )

    # Remove a versão anterior da Milk.
    catalogo_sem_milk = catalogo[
        catalogo["empresa"]
        != "Milk Distribuidora"
    ].copy()

    milk["embalagem_original"] = milk.apply(
        montar_embalagem,
        axis=1,
    )

    milk = milk.rename(
        columns={
            "produto_extraido":
                "produto_original",
            "produto_padronizado_inicial":
                "produto_normalizado",
            "quantidade_original":
                "quantidade",
            "unidade_original":
                "unidade",
            "quantidade_padronizada":
                "quantidade_base",
            "unidade_padronizada":
                "unidade_base",
            "data_catalogo":
                "data_referencia",
        }
    )

    milk["departamento"] = (
        "Não classificado na fonte"
    )

    milk["preco"] = pd.NA
    milk["preco_publico"] = False
    milk["link_produto"] = pd.NA

    # Garante o mesmo esquema do catálogo.
    for coluna in catalogo.columns:
        if coluna not in milk.columns:
            milk[coluna] = pd.NA

    milk = milk[catalogo.columns]

    catalogo_validado = pd.concat(
        [
            catalogo_sem_milk,
            milk,
        ],
        ignore_index=True,
    )

    duplicados_id = int(
        catalogo_validado[
            "id_registro"
        ]
        .duplicated()
        .sum()
    )

    catalogo_validado.to_csv(
        ARQUIVO_SAIDA,
        index=False,
        encoding="utf-8-sig",
    )

    print("Catálogo mestre reconstruído!")
    print(
        "Registros removidos da Milk antiga:",
        len(catalogo) - len(catalogo_sem_milk),
    )
    print(
        "Registros adicionados da Milk validada:",
        len(milk),
    )
    print(
        "Total final:",
        len(catalogo_validado),
    )
    print(
        "IDs duplicados:",
        duplicados_id,
    )
    print("Arquivo:", ARQUIVO_SAIDA)

    print("\nRegistros por empresa:")
    print(
        catalogo_validado[
            "empresa"
        ].value_counts()
    )


if __name__ == "__main__":
    main()