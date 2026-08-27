from datetime import datetime
from pathlib import Path

import pandas as pd


def main():
    data_coleta = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    fonte_segmentos = (
        "https://www.instagram.com/"
        "reel/C9Tcw5epWZO/"
    )

    fonte_aplicativo = (
        "https://apps.apple.com/br/app/"
        "wmix-atacado-e-varejo/"
        "id6547855846"
    )

    registros = [
        {
            "empresa": "WMix Ceará",
            "categoria_publica": "Confeitaria",
            "tipo_registro": "PERFIL_SEGMENTO",
            "nivel_detalhe": "CATEGORIA",
            "evidencia_publica":
                "Segmento informado em perfil público",
            "fonte": fonte_segmentos,
        },
        {
            "empresa": "WMix Ceará",
            "categoria_publica": "Sorveteria",
            "tipo_registro": "PERFIL_SEGMENTO",
            "nivel_detalhe": "CATEGORIA",
            "evidencia_publica":
                "Segmento informado em perfil público",
            "fonte": fonte_segmentos,
        },
        {
            "empresa": "WMix Ceará",
            "categoria_publica": "Açaí",
            "tipo_registro": "PERFIL_SEGMENTO",
            "nivel_detalhe": "CATEGORIA",
            "evidencia_publica":
                "Segmento informado em perfil público",
            "fonte": fonte_segmentos,
        },
        {
            "empresa": "WMix Ceará",
            "categoria_publica": "Food Service",
            "tipo_registro": "PERFIL_SEGMENTO",
            "nivel_detalhe": "CATEGORIA",
            "evidencia_publica":
                "Segmento informado em perfil público",
            "fonte": fonte_segmentos,
        },
        {
            "empresa": "WMix Ceará",
            "categoria_publica":
                "Insumos para confeitaria e sorveteria",
            "tipo_registro": "PERFIL_SEGMENTO",
            "nivel_detalhe": "CATEGORIA",
            "evidencia_publica":
                "Descrição pública do aplicativo",
            "fonte": fonte_aplicativo,
        },
    ]

    dados = pd.DataFrame(registros)

    dados["data_coleta"] = data_coleta
    dados["metodo_extracao"] = (
        "Curadoria de fonte pública"
    )
    dados["qualidade_extracao"] = "ALTA"

    arquivo = (
        Path("dados")
        / "tratados"
        / "perfil_publico_wmix.csv"
    )

    arquivo.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    dados.to_csv(
        arquivo,
        index=False,
        encoding="utf-8-sig",
    )

    print("Perfil público criado!")
    print("Registros:", len(dados))
    print("Arquivo:", arquivo)

    print("\nCategorias:")
    print(
        dados[
            "categoria_publica"
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()