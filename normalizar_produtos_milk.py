from pathlib import Path
import re

import pandas as pd


pasta_tratados = (
    Path("dados")
    / "tratados"
)

arquivo_entrada = (
    pasta_tratados
    / "produtos_milk_consolidados.csv"
)

arquivo_normalizado = (
    pasta_tratados
    / "produtos_milk_normalizados_iniciais.csv"
)

arquivo_revisao = (
    pasta_tratados
    / "produtos_milk_revisao.csv"
)

arquivo_qualidade = (
    pasta_tratados
    / "resumo_qualidade_milk.csv"
)


df = pd.read_csv(
    arquivo_entrada,
    dtype={"codigo_produto": str}
)

padrao_embalagem = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*"
    r"(KG|ML|G|L)\b",
    re.IGNORECASE
)


def extrair_embalagem(produto):
    produto = str(produto)

    resultados = padrao_embalagem.findall(
        produto
    )

    if not resultados:
        return {
            "quantidade_original": pd.NA,
            "unidade_original": pd.NA,
            "quantidade_padronizada": pd.NA,
            "unidade_padronizada": pd.NA
        }

    quantidade_texto, unidade = resultados[-1]

    quantidade = float(
        quantidade_texto.replace(",", ".")
    )

    unidade = unidade.upper()

    if unidade == "G":
        quantidade_padronizada = quantidade / 1000
        unidade_padronizada = "KG"

    elif unidade == "ML":
        quantidade_padronizada = quantidade / 1000
        unidade_padronizada = "L"

    else:
        quantidade_padronizada = quantidade
        unidade_padronizada = unidade

    return {
        "quantidade_original": quantidade,
        "unidade_original": unidade,
        "quantidade_padronizada": quantidade_padronizada,
        "unidade_padronizada": unidade_padronizada
    }


embalagens = (
    df["produto_extraido"]
    .apply(extrair_embalagem)
    .apply(pd.Series)
)

df = pd.concat(
    [df, embalagens],
    axis=1
)


df["produto_padronizado_inicial"] = (
    df["produto_extraido"]
    .str.replace(
        padrao_embalagem,
        "",
        regex=True
    )
    .str.replace(
        r"\s+",
        " ",
        regex=True
    )
    .str.strip(" .-")
)


def identificar_motivos(linha):
    motivos = []

    if linha["qualidade_extracao"] == "Média":
        motivos.append("Extração por coordenadas")

    if linha["codigo_valido"] == "Não":
        motivos.append("Código XX")

    if pd.isna(linha["quantidade_original"]):
        motivos.append("Embalagem não identificada")

    if "REVISAR" in str(
        linha["produto_extraido"]
    ).upper():
        motivos.append("Nome não identificado")

    return "; ".join(motivos)


df["motivos_revisao"] = df.apply(
    identificar_motivos,
    axis=1
)

df["revisao_necessaria"] = (
    df["motivos_revisao"]
    .apply(
        lambda texto: (
            "Sim" if texto else "Não"
        )
    )
)


total = len(df)

codigos_validos = (
    df["codigo_valido"] == "Sim"
).sum()

embalagens_identificadas = (
    df["quantidade_original"].notna()
).sum()

alta_confianca = (
    df["qualidade_extracao"] == "Alta"
).sum()

registros_revisao = (
    df["revisao_necessaria"] == "Sim"
).sum()

duplicados = df.duplicated(
    subset=[
        "pagina_catalogo",
        "codigo_produto",
        "produto_extraido"
    ]
).sum()


resumo = pd.DataFrame([
    {
        "indicador": "Total de registros",
        "quantidade": total,
        "percentual": 100
    },
    {
        "indicador": "Códigos válidos",
        "quantidade": codigos_validos,
        "percentual": codigos_validos / total * 100
    },
    {
        "indicador": "Embalagens identificadas",
        "quantidade": embalagens_identificadas,
        "percentual": (
            embalagens_identificadas
            / total
            * 100
        )
    },
    {
        "indicador": "Extração de alta confiança",
        "quantidade": alta_confianca,
        "percentual": alta_confianca / total * 100
    },
    {
        "indicador": "Registros para revisão",
        "quantidade": registros_revisao,
        "percentual": registros_revisao / total * 100
    },
    {
        "indicador": "Duplicidades exatas",
        "quantidade": duplicados,
        "percentual": duplicados / total * 100
    }
])


df.to_csv(
    arquivo_normalizado,
    index=False,
    encoding="utf-8-sig"
)

df[
    df["revisao_necessaria"] == "Sim"
].to_csv(
    arquivo_revisao,
    index=False,
    encoding="utf-8-sig"
)

resumo.to_csv(
    arquivo_qualidade,
    index=False,
    encoding="utf-8-sig"
)


print("Normalização inicial concluída!")
print(f"Registros analisados: {total}")

print("\nResumo da qualidade:")
print(
    resumo.to_string(
        index=False,
        formatters={
            "percentual": "{:.1f}%".format
        }
    )
)

print(
    f"\nBase normalizada: {arquivo_normalizado}"
)

print(
    f"Registros para revisão: {arquivo_revisao}"
)

print(
    f"Resumo da qualidade: {arquivo_qualidade}"
)