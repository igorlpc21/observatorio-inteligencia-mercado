import re
import unicodedata
from pathlib import Path

import pandas as pd


pasta_tratados = (
    Path("dados")
    / "tratados"
)

arquivo_milk = (
    pasta_tratados
    / "produtos_milk_normalizados_iniciais.csv"
)

arquivo_fortali = (
    pasta_tratados
    / "produtos_fortali_normalizados.csv"
)

arquivo_saida = (
    pasta_tratados
    / "catalogo_mestre_inicial.csv"
)


def normalizar_texto(texto):
    if pd.isna(texto):
        return pd.NA

    texto = unicodedata.normalize(
        "NFKD",
        str(texto)
    )

    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(
            caractere
        )
    )

    texto = texto.upper()

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


def obter_coluna(df, nomes):
    for nome in nomes:
        if nome in df.columns:
            return df[nome]

    return pd.Series(
        [pd.NA] * len(df),
        index=df.index,
        dtype="object"
    )


def status_milk(valor):
    if pd.isna(valor):
        return "Revisar"

    valor = str(valor).strip().upper()

    valores_negativos = {
        "NÃO",
        "NAO",
        "FALSE",
        "FALSO",
        "0"
    }

    if valor in valores_negativos:
        return "Pronto para comparar"

    return "Revisar"


try:
    # -------------------------
    # Carregamento
    # -------------------------

    milk = pd.read_csv(
        arquivo_milk,
        encoding="utf-8-sig",
        dtype={
            "codigo_produto": "string"
        }
    )

    fortali = pd.read_csv(
        arquivo_fortali,
        encoding="utf-8-sig",
        dtype={
            "codigo_produto": "string"
        }
    )

    print(
        f"Milk carregada: {len(milk)}"
    )

    print(
        f"Fortali carregada: {len(fortali)}"
    )

    # -------------------------
    # Padronização da Milk
    # -------------------------

    milk_padrao = pd.DataFrame(
        index=milk.index
    )

    milk_padrao["empresa"] = (
        "Milk Distribuidora"
    )

    milk_padrao["departamento"] = (
        "Catálogo geral"
    )

    milk_padrao["produto_original"] = (
        obter_coluna(
            milk,
            [
                "produto_extraido",
                "produto_original"
            ]
        )
    )

    milk_padrao["produto_normalizado"] = (
        milk_padrao["produto_original"]
        .apply(normalizar_texto)
    )

    milk_padrao["codigo_produto"] = (
        obter_coluna(
            milk,
            ["codigo_produto"]
        )
    )

    milk_padrao["codigo_valido"] = (
        obter_coluna(
            milk,
            ["codigo_valido"]
        )
    )

    milk_padrao["quantidade"] = (
        obter_coluna(
            milk,
            ["quantidade_original"]
        )
    )

    milk_padrao["unidade"] = (
        obter_coluna(
            milk,
            ["unidade_original"]
        )
    )

    milk_padrao["quantidade_base"] = (
        obter_coluna(
            milk,
            ["quantidade_padronizada"]
        )
    )

    milk_padrao["unidade_base"] = (
        obter_coluna(
            milk,
            [
                "unidade_padronizada",
                "unidade_base"
            ]
        )
    )

    milk_padrao["embalagem_original"] = (
        milk_padrao["quantidade"]
        .astype("string")
        .fillna("")
        + " "
        + milk_padrao["unidade"]
        .astype("string")
        .fillna("")
    ).str.strip()

    milk_padrao.loc[
        milk_padrao[
            "embalagem_original"
        ] == "",
        "embalagem_original"
    ] = pd.NA

    milk_padrao["preco"] = pd.NA

    milk_padrao["preco_publico"] = (
        "Não disponível"
    )

    milk_padrao["pagina_catalogo"] = (
        obter_coluna(
            milk,
            ["pagina_catalogo"]
        )
    )

    milk_padrao["data_referencia"] = (
        obter_coluna(
            milk,
            [
                "data_catalogo",
                "data_coleta"
            ]
        )
    )

    milk_padrao["metodo_extracao"] = (
        obter_coluna(
            milk,
            ["metodo_extracao"]
        )
    )

    milk_padrao["qualidade_extracao"] = (
        obter_coluna(
            milk,
            ["qualidade_extracao"]
        )
    )

    revisao_milk = obter_coluna(
        milk,
        ["revisao_necessaria"]
    )

    milk_padrao["status_validacao"] = (
        revisao_milk.apply(
            status_milk
        )
    )

    milk_padrao["link_produto"] = pd.NA

    milk_padrao["fonte"] = (
        obter_coluna(
            milk,
            ["fonte"]
        )
    )

    # -------------------------
    # Padronização da Fortali
    # -------------------------

    fortali_padrao = pd.DataFrame(
        index=fortali.index
    )

    fortali_padrao["empresa"] = (
        obter_coluna(
            fortali,
            ["empresa"]
        )
    )

    fortali_padrao["departamento"] = (
        obter_coluna(
            fortali,
            ["departamento"]
        )
    )

    fortali_padrao["produto_original"] = (
        obter_coluna(
            fortali,
            ["produto_original"]
        )
    )

    fortali_padrao["produto_normalizado"] = (
        obter_coluna(
            fortali,
            ["produto_normalizado"]
        )
    )

    fortali_padrao["codigo_produto"] = (
        obter_coluna(
            fortali,
            ["codigo_produto"]
        )
    )

    fortali_padrao["codigo_valido"] = (
        fortali_padrao[
            "codigo_produto"
        ].notna().map({
            True: "Sim",
            False: "Não"
        })
    )

    fortali_padrao["embalagem_original"] = (
        obter_coluna(
            fortali,
            ["embalagem_original"]
        )
    )

    fortali_padrao["quantidade"] = (
        obter_coluna(
            fortali,
            ["quantidade"]
        )
    )

    fortali_padrao["unidade"] = (
        obter_coluna(
            fortali,
            ["unidade"]
        )
    )

    fortali_padrao["quantidade_base"] = (
        obter_coluna(
            fortali,
            ["quantidade_base"]
        )
    )

    fortali_padrao["unidade_base"] = (
        obter_coluna(
            fortali,
            ["unidade_base"]
        )
    )

    fortali_padrao["preco"] = (
        obter_coluna(
            fortali,
            ["preco"]
        )
    )

    fortali_padrao["preco_publico"] = (
        obter_coluna(
            fortali,
            ["preco_publico"]
        )
    )

    fortali_padrao["pagina_catalogo"] = (
        obter_coluna(
            fortali,
            ["pagina_catalogo"]
        )
    )

    fortali_padrao["data_referencia"] = (
        obter_coluna(
            fortali,
            ["data_coleta"]
        )
    )

    fortali_padrao["metodo_extracao"] = (
        "Web scraping"
    )

    fortali_padrao["qualidade_extracao"] = (
        fortali[
            "status_validacao"
        ].apply(
            lambda valor: (
                "Alta"
                if valor
                == "Pronto para comparar"
                else "Revisar"
            )
        )
    )

    fortali_padrao["status_validacao"] = (
        obter_coluna(
            fortali,
            ["status_validacao"]
        )
    )

    fortali_padrao["link_produto"] = (
        obter_coluna(
            fortali,
            ["link_produto"]
        )
    )

    fortali_padrao["fonte"] = (
        obter_coluna(
            fortali,
            ["fonte"]
        )
    )

    # -------------------------
    # União das distribuidoras
    # -------------------------

    catalogo_mestre = pd.concat(
        [
            milk_padrao,
            fortali_padrao
        ],
        ignore_index=True
    )

        # -------------------------
    # Unidade-base universal
    # -------------------------

    catalogo_mestre[
        "quantidade_base"
    ] = pd.to_numeric(
        catalogo_mestre[
            "quantidade_base"
        ],
        errors="coerce"
    )

    catalogo_mestre[
        "unidade_base"
    ] = (
        catalogo_mestre[
            "unidade_base"
        ]
        .astype("string")
        .str.upper()
        .str.strip()
    )

    # Converte quilogramas para gramas.
    mascara_kg = (
        catalogo_mestre[
            "unidade_base"
        ]
        .eq("KG")
        .fillna(False)
    )

    catalogo_mestre.loc[
        mascara_kg,
        "quantidade_base"
    ] = (
        catalogo_mestre.loc[
            mascara_kg,
            "quantidade_base"
        ]
        * 1000
    )

    catalogo_mestre.loc[
        mascara_kg,
        "unidade_base"
    ] = "G"

    # Converte litros para mililitros.
    mascara_litro = (
        catalogo_mestre[
            "unidade_base"
        ]
        .eq("L")
        .fillna(False)
    )

    catalogo_mestre.loc[
        mascara_litro,
        "quantidade_base"
    ] = (
        catalogo_mestre.loc[
            mascara_litro,
            "quantidade_base"
        ]
        * 1000
    )

    catalogo_mestre.loc[
        mascara_litro,
        "unidade_base"
    ] = "ML"

    catalogo_mestre.insert(
        0,
        "id_registro",
        range(
            1,
            len(catalogo_mestre) + 1
        )
    )

    catalogo_mestre.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig"
    )

    # -------------------------
    # Resumo
    # -------------------------

    print("\nCatálogo mestre criado!")
    print(
        f"Total de registros: "
        f"{len(catalogo_mestre)}"
    )

    print(
        f"Arquivo salvo em: "
        f"{arquivo_saida}"
    )

    print("\nProdutos por empresa:")

    print(
        catalogo_mestre[
            "empresa"
        ]
        .value_counts()
        .to_string()
    )

    print("\nStatus por empresa:")

    resumo = pd.crosstab(
        catalogo_mestre["empresa"],
        catalogo_mestre[
            "status_validacao"
        ]
    )

    print(
        resumo.to_string()
    )


except FileNotFoundError as erro:
    print(
        f"Arquivo não encontrado: {erro}"
    )

except Exception as erro:
    print(
        f"Erro ao criar catálogo mestre: "
        f"{erro}"
    )