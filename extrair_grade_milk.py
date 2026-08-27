from pathlib import Path
import re

import pandas as pd
import pdfplumber


caminho_pdf = (
    Path("dados")
    / "catalogos"
    / "catalogo_milk_2022.pdf"
)

pasta_tratados = (
    Path("dados")
    / "tratados"
)

caminho_saida = (
    pasta_tratados
    / "produtos_milk_grade.csv"
)


def encontrar_codigos(palavras):
    codigos = []

    for palavra in palavras:
        texto = palavra["text"].lower().rstrip(".")

        if texto not in {"cód", "cod"}:
            continue

        candidatos = [
            outra
            for outra in palavras
            if abs(outra["top"] - palavra["top"]) < 4
            and outra["x0"] >= palavra["x1"] - 1
            and re.fullmatch(
                r"[A-Z0-9]+",
                outra["text"],
                re.IGNORECASE
            )
        ]

        if not candidatos:
            continue

        codigo = min(
            candidatos,
            key=lambda item: item["x0"]
        )

        codigos.append({
            "codigo": codigo["text"],
            "x": (
                palavra["x0"] + codigo["x1"]
            ) / 2,
            "top": palavra["top"]
        })

    return codigos


def agrupar_linhas(codigos, distancia=85):
    linhas = []

    for codigo in sorted(
        codigos,
        key=lambda item: item["top"]
    ):
        if not linhas:
            linhas.append([codigo])
            continue

        ultima_linha = linhas[-1]

        maior_posicao = max(
            item["top"]
            for item in ultima_linha
        )

        if codigo["top"] - maior_posicao > distancia:
            linhas.append([codigo])
        else:
            ultima_linha.append(codigo)

    return linhas


registros = []

with pdfplumber.open(caminho_pdf) as pdf:
    for numero_pagina, pagina in enumerate(
        pdf.pages,
        start=1
    ):
        if numero_pagina < 4:
            continue

        palavras = pagina.extract_words(
            x_tolerance=2,
            y_tolerance=3,
            use_text_flow=False
        )

        codigos = encontrar_codigos(
            palavras
        )

        linhas = agrupar_linhas(
            codigos
        )

        for linha in linhas:
            linha = sorted(
                linha,
                key=lambda item: item["x"]
            )

            posicoes = [
                item["x"]
                for item in linha
            ]

            limites = [0]

            for indice in range(
                len(posicoes) - 1
            ):
                ponto_medio = (
                    posicoes[indice]
                    + posicoes[indice + 1]
                ) / 2

                limites.append(ponto_medio)

            limites.append(pagina.width)

            maior_top = max(
                item["top"]
                for item in linha
            )

            for indice, codigo in enumerate(linha):
                limite_esquerdo = limites[indice]
                limite_direito = limites[indice + 1]

                palavras_celula = []

                for palavra in palavras:
                    centro_x = (
                        palavra["x0"]
                        + palavra["x1"]
                    ) / 2

                    dentro_horizontal = (
                        limite_esquerdo
                        <= centro_x
                        < limite_direito
                    )

                    dentro_vertical = (
                        maior_top - 165
                        <= palavra["top"]
                        < maior_top - 1
                    )

                    if (
                        dentro_horizontal
                        and dentro_vertical
                    ):
                        palavras_celula.append(
                            palavra
                        )

                palavras_celula = sorted(
                    palavras_celula,
                    key=lambda item: (
                        round(item["top"] / 3) * 3,
                        item["x0"]
                    )
                )

                textos = []

                for palavra in palavras_celula:
                    texto = palavra["text"]

                    if texto.lower().rstrip(".") in {
                        "cód",
                        "cod"
                    }:
                        continue

                    pertence_a_codigo = any(
                        texto == item["codigo"]
                        and abs(
                            palavra["top"]
                            - item["top"]
                        ) < 4
                        for item in linha
                    )

                    if pertence_a_codigo:
                        continue

                    textos.append(texto)

                produto = " ".join(textos)

                produto = re.sub(
                    r"(?:\.\s*){2,}",
                    " ",
                    produto
                )

                produto = " ".join(
                    produto.split()
                ).strip(" .-")

                if not produto:
                    produto = "REVISAR MANUALMENTE"

                registros.append({
                    "empresa": "Milk Distribuidora",
                    "produto_candidato": produto,
                    "codigo_produto": codigo["codigo"],
                    "pagina_catalogo": numero_pagina,
                    "metodo_extracao": "coordenadas_pdf",
                    "revisao_necessaria": "Sim",
                    "fonte": str(caminho_pdf)
                })


df_grade = pd.DataFrame(registros)

df_grade = df_grade.drop_duplicates(
    subset=[
        "pagina_catalogo",
        "codigo_produto"
    ]
)

df_grade.to_csv(
    caminho_saida,
    index=False,
    encoding="utf-8-sig"
)

print("Extração por coordenadas concluída!")
print(f"Registros encontrados: {len(df_grade)}")
print(f"Arquivo salvo em: {caminho_saida}")

print("\nExemplos encontrados:")
print(
    df_grade[
        [
            "produto_candidato",
            "codigo_produto",
            "pagina_catalogo"
        ]
    ]
    .head(20)
    .to_string(index=False)
)