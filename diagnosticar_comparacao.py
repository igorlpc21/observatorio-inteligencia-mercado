from pathlib import Path

import pandas as pd


arquivo = (
    Path("dados")
    / "tratados"
    / "catalogo_mestre_inicial.csv"
)


try:
    df = pd.read_csv(
        arquivo,
        encoding="utf-8-sig",
        dtype={
            "codigo_produto": "string"
        }
    )

    df["quantidade_base"] = pd.to_numeric(
        df["quantidade_base"],
        errors="coerce"
    )

    df["unidade_base"] = (
        df["unidade_base"]
        .astype("string")
        .str.upper()
        .str.strip()
    )

    print(
        f"Total de registros: {len(df)}"
    )

    print("\n=== COMPLETUDE POR EMPRESA ===")

    for empresa in df["empresa"].unique():
        base_empresa = df[
            df["empresa"] == empresa
        ]

        total = len(base_empresa)

        quantidade_valida = (
            base_empresa[
                "quantidade_base"
            ]
            .notna()
            .sum()
        )

        unidade_valida = (
            base_empresa[
                "unidade_base"
            ]
            .notna()
            .sum()
        )

        prontos = (
            base_empresa[
                "status_validacao"
            ]
            .eq("Pronto para comparar")
            .sum()
        )

        print(f"\nEmpresa: {empresa}")
        print(f"Total: {total}")

        print(
            f"Quantidade válida: "
            f"{quantidade_valida} "
            f"({quantidade_valida / total:.1%})"
        )

        print(
            f"Unidade válida: "
            f"{unidade_valida} "
            f"({unidade_valida / total:.1%})"
        )

        print(
            f"Prontos para comparar: "
            f"{prontos} "
            f"({prontos / total:.1%})"
        )

    print("\n=== UNIDADES ENCONTRADAS ===")

    resumo_unidades = pd.crosstab(
        df["unidade_base"],
        df["empresa"]
    )

    print(
        resumo_unidades.to_string()
    )

    # Criação da chave de embalagem.
    df_validos = df[
        df["quantidade_base"].notna()
        & df["unidade_base"].notna()
    ].copy()

    df_validos["chave_embalagem"] = (
        df_validos[
            "quantidade_base"
        ]
        .round(2)
        .astype(str)
        + " "
        + df_validos[
            "unidade_base"
        ]
    )

    milk = df_validos[
        df_validos["empresa"]
        == "Milk Distribuidora"
    ]

    fortali = df_validos[
        df_validos["empresa"]
        == "Fortali Distribuidora"
    ]

    embalagens_milk = set(
        milk["chave_embalagem"]
    )

    embalagens_fortali = set(
        fortali["chave_embalagem"]
    )

    embalagens_comuns = sorted(
        embalagens_milk
        .intersection(
            embalagens_fortali
        )
    )

    print(
        "\n=== EMBALAGENS EM COMUM "
        "USANDO TODOS OS REGISTROS ==="
    )

    print(
        f"Quantidade de embalagens comuns: "
        f"{len(embalagens_comuns)}"
    )

    for embalagem in embalagens_comuns[
        :20
    ]:
        print(embalagem)

    # Verificação somente dos produtos prontos.
    milk_prontos = milk[
        milk["status_validacao"]
        == "Pronto para comparar"
    ]

    fortali_prontos = fortali[
        fortali["status_validacao"]
        == "Pronto para comparar"
    ]

    chaves_milk_prontas = set(
        milk_prontos[
            "chave_embalagem"
        ]
    )

    chaves_fortali_prontas = set(
        fortali_prontos[
            "chave_embalagem"
        ]
    )

    embalagens_prontas_comuns = sorted(
        chaves_milk_prontas.intersection(
            chaves_fortali_prontas
        )
    )

    print(
        "\n=== EMBALAGENS EM COMUM "
        "SOMENTE ENTRE PRODUTOS PRONTOS ==="
    )

    print(
        f"Quantidade: "
        f"{len(embalagens_prontas_comuns)}"
    )

    for embalagem in (
        embalagens_prontas_comuns[:20]
    ):
        print(embalagem)

    print(
        "\n=== EXEMPLOS PRONTOS DA MILK ==="
    )

    print(
        milk_prontos[
            [
                "produto_original",
                "quantidade_base",
                "unidade_base"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )

    print(
        "\n=== EXEMPLOS PRONTOS DA FORTALI ==="
    )

    print(
        fortali_prontos[
            [
                "produto_original",
                "quantidade_base",
                "unidade_base"
            ]
        ]
        .head(10)
        .to_string(index=False)
    )


except FileNotFoundError:
    print(
        f"Arquivo não encontrado: {arquivo}"
    )

except Exception as erro:
    print(
        f"Erro durante o diagnóstico: "
        f"{erro}"
    )