import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

import pandas as pd


arquivo_entrada = (
    Path("dados")
    / "tratados"
    / "catalogo_mestre_inicial.csv"
)

arquivo_saida = (
    Path("dados")
    / "tratados"
    / "comparacoes_candidatas_milk_fortali.csv"
)


def normalizar_nome_comparacao(texto):
    if pd.isna(texto):
        return ""

    texto = str(texto).upper()

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

    # Remove medidas, pois elas serão
    # comparadas em colunas separadas.
    texto = re.sub(
        r"\d+(?:[.,]\d+)?\s*"
        r"(KG|ML|G|L)\b",
        " ",
        texto
    )

    texto = re.sub(
        r"[^A-Z0-9 ]",
        " ",
        texto
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto.strip()


def calcular_similaridade(
    nome_1,
    nome_2
):
    resultado = SequenceMatcher(
        None,
        nome_1,
        nome_2
    ).ratio()

    return round(
        resultado * 100,
        2
    )


def classificar_similaridade(valor):
    if valor >= 85:
        return "Alta"

    if valor >= 70:
        return "Média"

    return "Baixa"


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

    # Converte a quantidade para número.
    df["quantidade_base"] = (
        pd.to_numeric(
            df["quantidade_base"],
            errors="coerce"
        )
    )

    # Padroniza a unidade.
    df["unidade_base"] = (
        df["unidade_base"]
        .astype("string")
        .str.upper()
        .str.strip()
    )

    # Nome utilizado apenas no cálculo.
    df["nome_comparacao"] = (
        df["produto_original"]
        .apply(
            normalizar_nome_comparacao
        )
    )

        # Para descobrir candidatos, usamos
    # todos os registros com nome,
    # quantidade e unidade válidos.
    df_validos = df[
        df["produto_original"].notna()
        & df["quantidade_base"].notna()
        & df["unidade_base"].notna()
        & df["nome_comparacao"].ne("")
    ].copy()

    milk = df_validos[
        df_validos["empresa"]
        == "Milk Distribuidora"
    ].copy()

    fortali = df_validos[
        df_validos["empresa"]
        == "Fortali Distribuidora"
    ].copy()

    print(
        f"Produtos Milk disponíveis: "
        f"{len(milk)}"
    )

    print(
        f"Produtos Fortali disponíveis: "
        f"{len(fortali)}"
    )

    comparacoes = []

    for _, produto_milk in milk.iterrows():

        candidatos_fortali = fortali[
            (
                fortali["quantidade_base"]
                == produto_milk[
                    "quantidade_base"
                ]
            )
            &
            (
                fortali["unidade_base"]
                == produto_milk[
                    "unidade_base"
                ]
            )
        ]

        for _, produto_fortali in (
            candidatos_fortali.iterrows()
        ):
            similaridade = (
                calcular_similaridade(
                    produto_milk[
                        "nome_comparacao"
                    ],
                    produto_fortali[
                        "nome_comparacao"
                    ]
                )
            )

            # Valores abaixo de 55% não
            # serão considerados candidatos.
            if similaridade < 55:
                continue

            comparacoes.append({
                "id_milk": (
                    produto_milk[
                        "id_registro"
                    ]
                ),
                "produto_milk": (
                    produto_milk[
                        "produto_original"
                    ]
                ),
                "codigo_milk": (
                    produto_milk[
                        "codigo_produto"
                    ]
                ),
                "status_milk": (
                    produto_milk[
                        "status_validacao"
                    ]
                ),
                "id_fortali": (
                    produto_fortali[
                        "id_registro"
                    ]
                ),
                "produto_fortali": (
                    produto_fortali[
                        "produto_original"
                    ]
                ),
                "codigo_fortali": (
                    produto_fortali[
                        "codigo_produto"
                    ]
                ),
                "status_fortali": (
                    produto_fortali[
                        "status_validacao"
                    ]
                ),
                "quantidade_base": (
                    produto_milk[
                        "quantidade_base"
                    ]
                ),
                "unidade_base": (
                    produto_milk[
                        "unidade_base"
                    ]
                ),
                "similaridade_percentual": (
                    similaridade
                ),
                "classificacao": (
                    classificar_similaridade(
                        similaridade
                    )
                ),
                "equivalencia_confirmada": (
                    "Não"
                ),
                "revisao_humana": "Sim"
            })

    df_comparacoes = pd.DataFrame(
        comparacoes
    )

    if df_comparacoes.empty:
        print(
            "\nNenhuma comparação candidata "
            "foi encontrada."
        )

    else:
        # Ordena do mais semelhante
        # para o menos semelhante.
        df_comparacoes = (
            df_comparacoes
            .sort_values(
                by="similaridade_percentual",
                ascending=False
            )
        )

        # Mantém no máximo três opções
        # da Fortali para cada item Milk.
        df_comparacoes = (
            df_comparacoes
            .groupby(
                "id_milk",
                group_keys=False
            )
            .head(3)
            .reset_index(drop=True)
        )

        df_comparacoes.to_csv(
            arquivo_saida,
            index=False,
            encoding="utf-8-sig"
        )

        print(
            "\nBusca de semelhantes concluída!"
        )

        print(
            f"Candidatos encontrados: "
            f"{len(df_comparacoes)}"
        )

        print(
            f"Arquivo salvo em: "
            f"{arquivo_saida}"
        )

        print("\nClassificação:")

        print(
            df_comparacoes[
                "classificacao"
            ]
            .value_counts()
            .to_string()
        )

        print(
            "\nPrimeiras comparações:"
        )

        print(
            df_comparacoes[
                [
                    "produto_milk",
                    "produto_fortali",
                    "quantidade_base",
                    "unidade_base",
                    "similaridade_percentual",
                    "classificacao"
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
        f"Erro durante a comparação: "
        f"{erro}"
    )