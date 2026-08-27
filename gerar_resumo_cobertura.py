from pathlib import Path

import pandas as pd


PASTA = Path("dados") / "tratados"

FONTES = [
    {
        "empresa": "Milk Distribuidora",
        "arquivo": (
            PASTA
            / "produtos_milk_normalizados_iniciais.csv"
        ),
        "granularidade": "PRODUTO",
    },
    {
        "empresa": "Fortali Distribuidora",
        "arquivo": (
            PASTA
            / "produtos_fortali_normalizados.csv"
        ),
        "granularidade": "PRODUTO",
    },
    {
        "empresa": "Casa Garcia Gourmet",
        "arquivo": (
            PASTA
            / "produtos_casa_garcia_normalizados.csv"
        ),
        "granularidade": "PRODUTO",
    },
    {
        "empresa": "Safra Distribuidora",
        "arquivo": (
            PASTA
            / "portfolio_marcas_safra.csv"
        ),
        "granularidade": "MARCA",
    },
    {
        "empresa": "WMix Ceará",
        "arquivo": (
            PASTA
            / "perfil_publico_wmix.csv"
        ),
        "granularidade": "SEGMENTO",
    },
]


def contar_categorias(dados):
    for coluna in [
        "departamento",
        "categoria_publica",
        "categoria",
    ]:
        if coluna in dados.columns:
            return dados[coluna].nunique(
                dropna=True
            )

    return 0


def contar_itens_unicos(dados, granularidade):
    candidatos = {
        "PRODUTO": [
            "codigo_produto",
            "produto_normalizado",
            "produto_original",
        ],
        "MARCA": [
            "marca_fornecedor",
        ],
        "SEGMENTO": [
            "categoria_publica",
        ],
    }

    for coluna in candidatos[granularidade]:
        if coluna in dados.columns:
            return dados[coluna].nunique(
                dropna=True
            )

    return len(dados)


def contar_precos(dados):
    if "preco" not in dados.columns:
        return 0

    precos = pd.to_numeric(
        dados["preco"],
        errors="coerce",
    )

    return int(precos.notna().sum())


def classificar_cobertura(granularidade):
    if granularidade == "PRODUTO":
        return (
            "Catálogo detalhado; permite análises "
            "de variedade e correspondência"
        )

    if granularidade == "MARCA":
        return (
            "Portfólio de marcas; permite análises "
            "de presença e posicionamento"
        )

    return (
        "Perfil de segmentos; permite somente "
        "análise de posicionamento público"
    )


def main():
    resumo = []

    for fonte in FONTES:
        arquivo = fonte["arquivo"]

        if not arquivo.exists():
            print(
                "Arquivo não encontrado:",
                arquivo,
            )
            continue

        dados = pd.read_csv(arquivo)

        resumo.append({
            "empresa": fonte["empresa"],
            "arquivo": arquivo.name,
            "granularidade":
                fonte["granularidade"],
            "registros": len(dados),
            "itens_unicos": contar_itens_unicos(
                dados,
                fonte["granularidade"],
            ),
            "categorias_identificadas":
                contar_categorias(dados),
            "registros_com_preco":
                contar_precos(dados),
            "cobertura_analitica":
                classificar_cobertura(
                    fonte["granularidade"]
                ),
        })

    resultado = pd.DataFrame(resumo)

    arquivo_saida = (
        PASTA
        / "resumo_cobertura_fontes.csv"
    )

    resultado.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig",
    )

    print("Resumo de cobertura criado!")
    print("Empresas processadas:", len(resultado))
    print("Arquivo:", arquivo_saida)

    print("\nCobertura por empresa:\n")
    print(
        resultado[
            [
                "empresa",
                "granularidade",
                "registros",
                "itens_unicos",
                "categorias_identificadas",
                "registros_com_preco",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()