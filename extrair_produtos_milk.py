from datetime import datetime
from pathlib import Path
import re

import pandas as pd
import pdfplumber


empresa = "Milk Distribuidora"

caminho_pdf = (
    Path("dados")
    / "catalogos"
    / "catalogo_milk_2022.pdf"
)

pasta_tratados = (
    Path("dados")
    / "tratados"
)

pasta_tratados.mkdir(
    exist_ok=True
)

caminho_saida = (
    pasta_tratados
    / "produtos_milk_candidatos.csv"
)

padrao_produto = re.compile(
    r"([A-ZÀ-ÖØ-Ý0-9]"
    r"[A-ZÀ-ÖØ-Ý0-9ÇÃÕÁÉÍÓÚÂÊÔÜ "
    r",/()•%\-]*?)"
    r"\s*(?:\.\s*){2,}"
    r"cód\s*([A-Z0-9]+)",
    re.IGNORECASE
)

registros = []

with pdfplumber.open(caminho_pdf) as pdf:
    for numero_pagina, pagina in enumerate(
        pdf.pages,
        start=1
    ):
        texto = pagina.extract_text(
            x_tolerance=2,
            y_tolerance=3
        )

        if not texto:
            continue

        resultados = padrao_produto.findall(
            texto
        )

        for produto, codigo in resultados:
            produto_limpo = " ".join(
                produto.split()
            )

            produto_limpo = produto_limpo.strip(
                " .-"
            )

            registros.append({
                "empresa": empresa,
                "produto_original": produto_limpo,
                "codigo_produto": codigo,
                "pagina_catalogo": numero_pagina,
                "data_catalogo": "2022-02-14",
                "data_extracao": (
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ),
                "metodo_extracao": "lista_pontilhada",
                "revisao_necessaria": "Sim",
                "fonte": str(caminho_pdf)
            })

df_produtos = pd.DataFrame(
    registros
)

df_produtos = df_produtos.drop_duplicates(
    subset=[
        "produto_original",
        "codigo_produto"
    ]
)

df_produtos = df_produtos.sort_values(
    by=[
        "pagina_catalogo",
        "codigo_produto"
    ]
)

df_produtos.to_csv(
    caminho_saida,
    index=False,
    encoding="utf-8-sig"
)

print("Extração de candidatos concluída!")
print(f"Produtos reconhecidos: {len(df_produtos)}")
print(f"Arquivo salvo em: {caminho_saida}")

print("\nPrimeiros produtos:")
print(
    df_produtos[
        [
            "produto_original",
            "codigo_produto",
            "pagina_catalogo"
        ]
    ]
    .head(15)
    .to_string(index=False)
)