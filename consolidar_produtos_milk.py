from pathlib import Path

import pandas as pd


pasta_tratados = (
    Path("dados")
    / "tratados"
)

arquivo_lista = (
    pasta_tratados
    / "produtos_milk_candidatos.csv"
)

arquivo_grade = (
    pasta_tratados
    / "produtos_milk_grade.csv"
)

arquivo_saida = (
    pasta_tratados
    / "produtos_milk_consolidados.csv"
)


df_lista = pd.read_csv(
    arquivo_lista,
    dtype={"codigo_produto": str}
)

df_grade = pd.read_csv(
    arquivo_grade,
    dtype={"codigo_produto": str}
)


df_lista = df_lista.rename(
    columns={
        "produto_original": "produto_extraido"
    }
)

df_grade = df_grade.rename(
    columns={
        "produto_candidato": "produto_extraido"
    }
)


df_lista["prioridade_metodo"] = 1
df_lista["qualidade_extracao"] = "Alta"

df_grade["prioridade_metodo"] = 2
df_grade["qualidade_extracao"] = "Média"

df_grade["data_catalogo"] = "2022-02-14"


df_completo = pd.concat(
    [
        df_lista,
        df_grade
    ],
    ignore_index=True
)


def criar_chave(linha):
    pagina = str(
        linha["pagina_catalogo"]
    )

    codigo = str(
        linha["codigo_produto"]
    ).upper()

    produto = str(
        linha["produto_extraido"]
    ).upper()

    if codigo == "XX":
        return (
            pagina
            + "-"
            + codigo
            + "-"
            + produto
        )

    return pagina + "-" + codigo


df_completo["chave_produto"] = (
    df_completo.apply(
        criar_chave,
        axis=1
    )
)


df_completo = df_completo.sort_values(
    by="prioridade_metodo"
)

df_consolidado = (
    df_completo
    .drop_duplicates(
        subset=["chave_produto"],
        keep="first"
    )
    .copy()
)


df_consolidado["codigo_valido"] = (
    df_consolidado["codigo_produto"]
    .apply(
        lambda codigo: (
            "Não"
            if str(codigo).upper() == "XX"
            else "Sim"
        )
    )
)


df_consolidado = df_consolidado.sort_values(
    by=[
        "pagina_catalogo",
        "codigo_produto"
    ]
)


colunas_saida = [
    "empresa",
    "produto_extraido",
    "codigo_produto",
    "codigo_valido",
    "pagina_catalogo",
    "data_catalogo",
    "metodo_extracao",
    "qualidade_extracao",
    "revisao_necessaria",
    "fonte"
]

df_consolidado[colunas_saida].to_csv(
    arquivo_saida,
    index=False,
    encoding="utf-8-sig"
)


total_catalogo = 144
total_extraido = len(df_consolidado)

cobertura = (
    total_extraido
    / total_catalogo
    * 100
)


print("Consolidação concluída!")
print(f"Produtos consolidados: {total_extraido}")
print(f"Cobertura estimada: {cobertura:.1f}%")
print(f"Arquivo salvo em: {arquivo_saida}")

print("\nQualidade da extração:")
print(
    df_consolidado[
        "qualidade_extracao"
    ].value_counts()
)