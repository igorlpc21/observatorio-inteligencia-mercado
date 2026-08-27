from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PASTA_TRATADOS = Path("dados") / "tratados"
PASTA_GRAFICOS = Path("graficos")

CATALOGO = (
    PASTA_TRATADOS
    / "catalogo_mestre_validado.csv"
)

SAFRA = (
    PASTA_TRATADOS
    / "portfolio_marcas_safra.csv"
)

WMIX = (
    PASTA_TRATADOS
    / "perfil_publico_wmix.csv"
)

ARQUIVO_INDICADORES = (
    PASTA_TRATADOS
    / "indicadores_observatorio.csv"
)

COR_PRINCIPAL = "#2563EB"
COR_TEXTO = "#1F2937"
COR_GRADE = "#E5E7EB"


def preenchido(serie):
    texto = (
        serie
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return ~texto.isin(
        ["", "nan", "none", "null"]
    )


def taxa_booleano_verdadeiro(dados, coluna):
    if coluna not in dados.columns:
        return pd.NA

    valores = (
        dados[coluna]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    verdadeiros = valores.isin(
        ["true", "1", "sim", "yes"]
    )

    return round(
        verdadeiros.mean() * 100,
        2,
    )


def categorias_validas(dados):
    if "departamento" not in dados.columns:
        return 0

    categorias = (
        dados["departamento"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    categorias = categorias[
        ~categorias.str.lower().isin([
            "",
            "nan",
            "none",
            "null",
            "não classificado na fonte",
            "nao classificado na fonte",
        ])
    ]

    return categorias.nunique()


def criar_indicadores():
    catalogo = pd.read_csv(
        CATALOGO,
        dtype={
            "id_registro": "string",
            "codigo_produto": "string",
        },
    )

    indicadores = []

    for empresa, dados in catalogo.groupby(
        "empresa"
    ):
        total = len(dados)

        medidas_preenchidas = int(
            preenchido(
                dados["quantidade_base"]
            ).sum()
        )

        precos_preenchidos = int(
            preenchido(
                dados["preco"]
            ).sum()
        )

        indicadores.append({
            "empresa": empresa,
            "nivel_dado": "PRODUTO",
            "registros_publicos": total,
            "itens_unicos":
                dados["id_registro"].nunique(),
            "categorias_identificadas":
                categorias_validas(dados),
            "taxa_medida_preenchida_pct":
                round(
                    medidas_preenchidas
                    / total
                    * 100,
                    2,
                ),
            "taxa_codigo_valido_pct":
                taxa_booleano_verdadeiro(
                    dados,
                    "codigo_valido",
                ),
            "registros_com_preco":
                precos_preenchidos,
            "escopo_comparavel":
                "Variedade, nomes e embalagens",
        })

    safra = pd.read_csv(SAFRA)

    indicadores.append({
        "empresa": "Safra Distribuidora",
        "nivel_dado": "MARCA",
        "registros_publicos": len(safra),
        "itens_unicos":
            safra["marca_fornecedor"].nunique(),
        "categorias_identificadas":
            safra["categoria_publica"].nunique(),
        "taxa_medida_preenchida_pct": pd.NA,
        "taxa_codigo_valido_pct": pd.NA,
        "registros_com_preco": 0,
        "escopo_comparavel":
            "Presença de marcas e segmentos",
    })

    wmix = pd.read_csv(WMIX)

    indicadores.append({
        "empresa": "WMix Ceará",
        "nivel_dado": "SEGMENTO",
        "registros_publicos": len(wmix),
        "itens_unicos":
            wmix["categoria_publica"].nunique(),
        "categorias_identificadas":
            wmix["categoria_publica"].nunique(),
        "taxa_medida_preenchida_pct": pd.NA,
        "taxa_codigo_valido_pct": pd.NA,
        "registros_com_preco": 0,
        "escopo_comparavel":
            "Posicionamento público por segmento",
    })

    return pd.DataFrame(indicadores)


def configurar_eixo(ax):
    ax.spines[
        ["top", "right", "left"]
    ].set_visible(False)

    ax.spines["bottom"].set_color(
        COR_GRADE
    )

    ax.grid(
        axis="x",
        color=COR_GRADE,
        linewidth=0.8,
    )

    ax.set_axisbelow(True)
    ax.tick_params(
        colors=COR_TEXTO
    )


def grafico_cobertura(indicadores):
    dados = (
        indicadores[
            indicadores["nivel_dado"]
            == "PRODUTO"
        ]
        .sort_values("registros_publicos")
    )

    fig, ax = plt.subplots(
        figsize=(10, 5.5)
    )

    barras = ax.barh(
        dados["empresa"],
        dados["registros_publicos"],
        color=COR_PRINCIPAL,
    )

    ax.bar_label(
        barras,
        padding=5,
        fmt="%.0f",
        color=COR_TEXTO,
    )

    ax.set_title(
        "Registros de produtos disponíveis por catálogo público",
        loc="left",
        fontsize=14,
        weight="bold",
        color=COR_TEXTO,
        pad=18,
    )

    ax.set_xlabel(
        "Quantidade de registros públicos"
    )

    configurar_eixo(ax)

    fig.text(
        0.125,
        0.01,
        (
            "Nota: o volume representa cobertura "
            "da fonte pública, não tamanho ou "
            "desempenho da empresa."
        ),
        fontsize=9,
        color="#6B7280",
    )

    plt.tight_layout(
        rect=[0, 0.06, 1, 1]
    )

    plt.savefig(
        PASTA_GRAFICOS
        / "cobertura_catalogos_produtos.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def grafico_completude(indicadores):
    dados = (
        indicadores[
            indicadores["nivel_dado"]
            == "PRODUTO"
        ]
        .dropna(
            subset=[
                "taxa_medida_preenchida_pct"
            ]
        )
        .sort_values(
            "taxa_medida_preenchida_pct"
        )
    )

    fig, ax = plt.subplots(
        figsize=(10, 5.5)
    )

    barras = ax.barh(
        dados["empresa"],
        dados[
            "taxa_medida_preenchida_pct"
        ],
        color=COR_PRINCIPAL,
    )

    ax.bar_label(
        barras,
        padding=5,
        fmt="%.1f%%",
        color=COR_TEXTO,
    )

    ax.set_xlim(0, 100)

    ax.set_title(
        "Completude de peso ou volume padronizado",
        loc="left",
        fontsize=14,
        weight="bold",
        color=COR_TEXTO,
        pad=18,
    )

    ax.set_xlabel(
        "Percentual dos registros"
    )

    configurar_eixo(ax)

    fig.text(
        0.125,
        0.01,
        (
            "Produtos sem medida permanecem "
            "válidos para análises por nome, "
            "mas não para equivalência de embalagem."
        ),
        fontsize=9,
        color="#6B7280",
    )

    plt.tight_layout(
        rect=[0, 0.06, 1, 1]
    )

    plt.savefig(
        PASTA_GRAFICOS
        / "completude_medidas_produtos.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close()


def main():
    PASTA_GRAFICOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    indicadores = criar_indicadores()

    indicadores.to_csv(
        ARQUIVO_INDICADORES,
        index=False,
        encoding="utf-8-sig",
    )

    grafico_cobertura(indicadores)
    grafico_completude(indicadores)

    print("Indicadores criados!")
    print("Arquivo:", ARQUIVO_INDICADORES)

    print("\nResumo:\n")
    print(
        indicadores.to_string(
            index=False
        )
    )

    print("\nGráficos:")
    print(
        PASTA_GRAFICOS
        / "cobertura_catalogos_produtos.png"
    )
    print(
        PASTA_GRAFICOS
        / "completude_medidas_produtos.png"
    )


if __name__ == "__main__":
    main()