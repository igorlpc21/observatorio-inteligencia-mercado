import re
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup, NavigableString


URL = (
    "https://www.distribuidorasafra.com.br/"
    "fornecedores.php"
)

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "Chrome/131.0 Safari/537.36"
    )
}

CATEGORIAS = {
    "panificacao e confeitaria":
        "Panificação e Confeitaria",
    "sorveteria":
        "Sorveteria",
    "food service":
        "Food Service",
}


def normalizar(texto):
    texto = unicodedata.normalize(
        "NFD",
        str(texto),
    )

    texto = "".join(
        caractere
        for caractere in texto
        if unicodedata.category(caractere) != "Mn"
    )

    texto = re.sub(
        r"\s+",
        " ",
        texto,
    )

    return texto.strip().lower()


def localizar_categoria(imagem):
    for elemento in imagem.previous_elements:
        if not isinstance(
            elemento,
            NavigableString,
        ):
            continue

        texto = normalizar(elemento)

        for chave, categoria in CATEGORIAS.items():
            if chave in texto:
                return categoria

    return "Não identificada"


def main():
    resposta = requests.get(
        URL,
        headers=CABECALHOS,
        timeout=30,
    )

    print("Status HTTP:", resposta.status_code)

    resposta.raise_for_status()

    soup = BeautifulSoup(
        resposta.text,
        "html.parser",
    )

    fornecedores = []

    for imagem in soup.find_all("img"):
        origem = imagem.get(
            "src",
            "",
        ).strip()

        # Seleciona somente miniaturas da pasta
        # pública de fornecedores.
        if not re.search(
            r"(?:^|/)fornecedores/tn_",
            origem,
            flags=re.IGNORECASE,
        ):
            continue

        nome = (
            imagem.get("alt", "").strip()
            or imagem.get("title", "").strip()
        )

        if not nome:
            continue

        fornecedores.append({
            "empresa": "Safra Distribuidora",
            "categoria_publica": localizar_categoria(
                imagem
            ),
            "marca_fornecedor": nome.upper(),
            "tipo_registro": "PORTFOLIO_MARCA",
            "nivel_detalhe": "MARCA",
            "url_imagem": urljoin(
                URL,
                origem,
            ),
            "data_coleta": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "fonte": URL,
        })

    dados = pd.DataFrame(fornecedores)

    if dados.empty:
        print("Nenhum fornecedor foi coletado.")
        return

    dados = dados.drop_duplicates(
        subset=["marca_fornecedor"]
    )

    dados = dados.sort_values(
        by=[
            "categoria_publica",
            "marca_fornecedor",
        ]
    )

    pasta_saida = (
        Path("dados")
        / "tratados"
    )

    pasta_saida.mkdir(
        parents=True,
        exist_ok=True,
    )

    arquivo_saida = (
        pasta_saida
        / "portfolio_marcas_safra.csv"
    )

    dados.to_csv(
        arquivo_saida,
        index=False,
        encoding="utf-8-sig",
    )

    print("\nColeta concluída!")
    print("Marcas coletadas:", len(dados))
    print("Arquivo:", arquivo_saida)

    print("\nMarcas por categoria:")
    print(
        dados[
            "categoria_publica"
        ].value_counts()
    )

    print("\nFornecedores:")
    print(
        dados[
            [
                "categoria_publica",
                "marca_fornecedor",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as erro:
        print("Erro de acesso:", erro)

    except Exception as erro:
        print("Erro durante a coleta:", erro)