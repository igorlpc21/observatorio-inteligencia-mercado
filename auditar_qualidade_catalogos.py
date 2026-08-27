from pathlib import Path

import pandas as pd


PASTA = Path("dados") / "tratados"

BASES = [
    {
        "empresa": "Milk Distribuidora",
        "arquivo": (
            PASTA
            / "produtos_milk_normalizados_iniciais.csv"
        ),
        "chave": ["codigo_produto"],
    },
    {
        "empresa": "Fortali Distribuidora",
        "arquivo": (
            PASTA
            / "produtos_fortali_normalizados.csv"
        ),
        "chave": ["codigo_produto"],
    },
    {
        "empresa": "Casa Garcia Gourmet",
        "arquivo": (
            PASTA
            / "produtos_casa_garcia_normalizados.csv"
        ),
        "chave": [
            "departamento",
            "codigo_produto",
        ],
    },
]


def serie_vazia(serie):
    return (
        serie.isna()
        | serie.astype(str).str.strip().eq("")
        | serie.astype(str).str.lower().isin(
            ["nan", "none", "null"]
        )
    )


def localizar_coluna(dados, candidatos):
    for coluna in candidatos:
        if coluna in dados.columns:
            return coluna

    return None


def main():
    resumo = []
    duplicados_encontrados = []

    for configuracao in BASES:
        empresa = configuracao["empresa"]
        arquivo = configuracao["arquivo"]
        chave = configuracao["chave"]

        dados = pd.read_csv(
            arquivo,
            dtype="string",
        )

        coluna_nome = localizar_coluna(
            dados,
            [
                "produto_original",
                "produto_extraido",
                "produto_normalizado",
            ],
        )

        coluna_categoria = localizar_coluna(
            dados,
            [
                "departamento",
                "categoria_publica",
                "categoria",
            ],
        )

        chaves_validas = pd.Series(
            True,
            index=dados.index,
        )

        for coluna in chave:
            chaves_validas &= ~serie_vazia(
                dados[coluna]
            )

        mascara_duplicados = (
            dados.duplicated(
                subset=chave,
                keep=False,
            )
            & chaves_validas
        )

        registros_duplicados = dados[
            mascara_duplicados
        ].copy()

        if not registros_duplicados.empty:
            registros_duplicados.insert(
                0,
                "empresa_auditoria",
                empresa,
            )

            duplicados_encontrados.append(
                registros_duplicados
            )

        chaves_vazias = int(
            (~chaves_validas).sum()
        )

        nomes_vazios = (
            int(
                serie_vazia(
                    dados[coluna_nome]
                ).sum()
            )
            if coluna_nome
            else len(dados)
        )

        categorias_unicas = (
            dados[coluna_categoria]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .nunique()
            if coluna_categoria
            else 0
        )

        medida_preenchida = 0

        if "quantidade_base" in dados.columns:
            medida_preenchida = int(
                (~serie_vazia(
                    dados["quantidade_base"]
                )).sum()
            )

        resumo.append({
            "empresa": empresa,
            "registros": len(dados),
            "duplicados_exatos":
                int(dados.duplicated().sum()),
            "registros_com_chave_duplicada":
                int(mascara_duplicados.sum()),
            "chaves_vazias": chaves_vazias,
            "nomes_vazios": nomes_vazios,
            "categorias_unicas":
                categorias_unicas,
            "medidas_preenchidas":
                medida_preenchida,
            "taxa_medida_preenchida_pct":
                round(
                    medida_preenchida
                    / len(dados)
                    * 100,
                    2,
                ),
        })

        print("\n" + "=" * 60)
        print(empresa)
        print("=" * 60)

        if coluna_categoria:
            print("Categorias encontradas:")
            print(
                dados[coluna_categoria]
                .value_counts(
                    dropna=False
                )
                .to_string()
            )
        else:
            print(
                "A base não possui coluna de categoria."
            )

    resumo_df = pd.DataFrame(resumo)

    arquivo_resumo = (
        PASTA
        / "auditoria_qualidade_catalogos.csv"
    )

    resumo_df.to_csv(
        arquivo_resumo,
        index=False,
        encoding="utf-8-sig",
    )

    arquivo_duplicados = (
        PASTA
        / "registros_chave_duplicada.csv"
    )

    if duplicados_encontrados:
        pd.concat(
            duplicados_encontrados,
            ignore_index=True,
        ).to_csv(
            arquivo_duplicados,
            index=False,
            encoding="utf-8-sig",
        )

    print("\n" + "=" * 60)
    print("RESUMO DA AUDITORIA")
    print("=" * 60)

    print(
        resumo_df.to_string(
            index=False
        )
    )

    print("\nArquivo:", arquivo_resumo)

    if duplicados_encontrados:
        print(
            "Detalhes das chaves duplicadas:",
            arquivo_duplicados,
        )
    else:
        print(
            "Nenhuma chave duplicada encontrada."
        )


if __name__ == "__main__":
    main()