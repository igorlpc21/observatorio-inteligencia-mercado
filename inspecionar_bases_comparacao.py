from pathlib import Path

import pandas as pd


arquivos = {
    "Milk Distribuidora": (
        Path("dados")
        / "tratados"
        / "produtos_milk_normalizados_iniciais.csv"
    ),

    "Fortali Distribuidora": (
        Path("dados")
        / "tratados"
        / "produtos_fortali_normalizados.csv"
    )
}


for empresa, caminho in arquivos.items():
    print("\n" + "=" * 70)
    print(f"EMPRESA: {empresa}")
    print(f"ARQUIVO: {caminho}")
    print("=" * 70)

    try:
        df = pd.read_csv(
            caminho,
            encoding="utf-8-sig"
        )

        print(
            f"\nQuantidade de registros: "
            f"{len(df)}"
        )

        print(
            f"Quantidade de colunas: "
            f"{len(df.columns)}"
        )

        print("\nColunas encontradas:")

        for numero, coluna in enumerate(
            df.columns,
            start=1
        ):
            print(
                f"{numero}. {coluna}"
            )

        print("\nExemplo de valor por coluna:")

        for coluna in df.columns:
            valores_validos = (
                df[coluna]
                .dropna()
            )

            if not valores_validos.empty:
                exemplo = str(
                    valores_validos.iloc[0]
                )
            else:
                exemplo = "SEM VALOR"

            print(
                f"{coluna}: "
                f"{exemplo[:120]}"
            )

    except FileNotFoundError:
        print(
            "\nArquivo não encontrado."
        )

    except Exception as erro:
        print(
            f"\nErro ao ler o arquivo: "
            f"{erro}"
        )