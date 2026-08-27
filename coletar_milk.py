from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup


empresa = "Milk Distribuidora"
url = "https://milkdistribuidora.com.br/"

cabecalhos = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/151.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
    "Upgrade-Insecure-Requests": "1"
}

titulos_ignorados = {
    "CONHEÇA NOSSOS",
    "PRODUTOS",
    "SOBRE NÓS"
}

try:
    resposta = requests.get(
        url,
        headers=cabecalhos,
        timeout=20
    )

    resposta.raise_for_status()

    pagina = BeautifulSoup(
        resposta.text,
        "html.parser"
    )

    registros = []
    data_coleta = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    elementos = pagina.find_all(
        ["h1", "h2", "h3", "h4"]
    )

    for elemento in elementos:
        texto = elemento.get_text(
            " ",
            strip=True
        )

        texto_maiusculo = texto.upper()

        if not texto:
            continue

        if texto_maiusculo in titulos_ignorados:
            continue

        if texto_maiusculo.startswith("SIGA A GENTE"):
            continue

        registros.append({
            "empresa": empresa,
            "categoria": texto,
            "data_coleta": data_coleta,
            "fonte": url
        })

    df_categorias = pd.DataFrame(registros)

    df_categorias = df_categorias.drop_duplicates(
        subset=["empresa", "categoria"]
    )

    caminho_saida = (
        Path("dados") / "categorias_milk.csv"
    )

    df_categorias.to_csv(
        caminho_saida,
        index=False,
        encoding="utf-8-sig"
    )

    print("Coleta concluída com sucesso!")
    print(f"Registros coletados: {len(df_categorias)}")
    print(f"Arquivo salvo em: {caminho_saida}")

    print("\nCategorias coletadas:")
    print(df_categorias.to_string(index=False))

except requests.RequestException as erro:
    print(f"Erro de acesso ao site: {erro}")

except Exception as erro:
    print(f"Erro durante o tratamento: {erro}")