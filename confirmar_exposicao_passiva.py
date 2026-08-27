from datetime import datetime
from hashlib import sha256
from pathlib import Path
from urllib.parse import urljoin
import re

import requests
from bs4 import BeautifulSoup


SITE = "https://mercadodosabor.com.br/"

ARQUIVO_JS = (
    "https://mercadodosabor.com.br/"
    "static/js/main.1fab0e69.chunk.js"
)

PASTA_RELATORIOS = Path("relatorios")

ARQUIVO_RELATORIO = (
    PASTA_RELATORIOS
    / "confirmacao_passiva_mercado_sabor.txt"
)

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "PassiveSecurityVerification/1.0"
    )
}


def hash_completo(conteudo):
    return sha256(conteudo).hexdigest()


def hash_parcial(valor):
    return sha256(
        valor.encode("utf-8")
    ).hexdigest()[:16]


def cabecalho_seguro(resposta, nome):
    return resposta.headers.get(
        nome,
        "Não informado"
    )


def localizar_campos(texto):
    padroes = {
        "Auth-Token": {
            "regex": (
                r'["\']Auth-Token["\']'
                r'\s*:\s*["\']([^"\']+)'
            ),
            "classificacao": (
                "Potencial credencial"
            ),
        },
        "client_id": {
            "regex": (
                r'client_id\s*:\s*'
                r'["\']([^"\']+)'
            ),
            "classificacao": (
                "Identificador OAuth"
            ),
        },
        "client_secret": {
            "regex": (
                r'client_secret\s*:\s*'
                r'["\']([^"\']+)'
            ),
            "classificacao": (
                "Potencial segredo OAuth"
            ),
        },
        "Firebase apiKey": {
            "regex": (
                r'apiKey\s*:\s*'
                r'["\']([^"\']+)'
            ),
            "classificacao": (
                "Configuração pública a revisar"
            ),
        },
        "Chave fixa de criptografia": {
            "regex": (
                r'(?:aes\.decrypt|decrypt)'
                r'\s*\([^,]+,\s*'
                r'["\']([^"\']+)'
            ),
            "classificacao": (
                "Material criptográfico no frontend"
            ),
        },
    }

    resultados = []

    for campo, configuracao in padroes.items():
        valores = re.findall(
            configuracao["regex"],
            texto,
            flags=re.IGNORECASE,
        )

        valores_unicos = list(dict.fromkeys(valores))

        if not valores_unicos:
            resultados.append({
                "campo": campo,
                "encontrado": False,
                "quantidade": 0,
                "tamanho": "-",
                "hash": "-",
                "classificacao": (
                    configuracao["classificacao"]
                ),
            })

            continue

        for valor in valores_unicos:
            resultados.append({
                "campo": campo,
                "encontrado": True,
                "quantidade": len(valores),
                "tamanho": len(valor),
                "hash": hash_parcial(valor),
                "classificacao": (
                    configuracao["classificacao"]
                ),
            })

    return resultados


def main():
    PASTA_RELATORIOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    linhas = []

    data_verificacao = datetime.now().astimezone()

    linhas.append(
        "CONFIRMAÇÃO PASSIVA DE EXPOSIÇÃO"
    )
    linhas.append("=" * 60)
    linhas.append(
        f"Data: {data_verificacao:%d/%m/%Y %H:%M:%S %z}"
    )
    linhas.append(f"Site: {SITE}")
    linhas.append(f"JavaScript: {ARQUIVO_JS}")
    linhas.append("")

    print("Consultando somente recursos públicos...")

    resposta_site = requests.get(
        SITE,
        headers=CABECALHOS,
        timeout=30,
        allow_redirects=True,
    )

    linhas.append("1. PÁGINA PRINCIPAL")
    linhas.append(
        f"Status HTTP: {resposta_site.status_code}"
    )
    linhas.append(
        f"URL final: {resposta_site.url}"
    )
    linhas.append(
        "Content-Type: "
        + cabecalho_seguro(
            resposta_site,
            "Content-Type",
        )
    )

    soup = BeautifulSoup(
        resposta_site.text,
        "html.parser",
    )

    scripts = []

    for elemento in soup.find_all(
        "script",
        src=True,
    ):
        scripts.append(
            urljoin(
                resposta_site.url,
                elemento["src"],
            )
        )

    javascript_carregado = (
        ARQUIVO_JS in scripts
    )

    linhas.append(
        "JavaScript referenciado pelo site: "
        + ("SIM" if javascript_carregado else "NÃO")
    )
    linhas.append(
        f"Scripts públicos encontrados: {len(scripts)}"
    )
    linhas.append("")

    resposta_js = requests.get(
        ARQUIVO_JS,
        headers=CABECALHOS,
        timeout=30,
        allow_redirects=True,
    )

    linhas.append("2. ARQUIVO JAVASCRIPT")
    linhas.append(
        f"Status HTTP: {resposta_js.status_code}"
    )
    linhas.append(
        f"URL final: {resposta_js.url}"
    )
    linhas.append(
        f"Tamanho: {len(resposta_js.content)} bytes"
    )
    linhas.append(
        "Content-Type: "
        + cabecalho_seguro(
            resposta_js,
            "Content-Type",
        )
    )
    linhas.append(
        "ETag: "
        + cabecalho_seguro(
            resposta_js,
            "ETag",
        )
    )
    linhas.append(
        "Last-Modified: "
        + cabecalho_seguro(
            resposta_js,
            "Last-Modified",
        )
    )
    linhas.append(
        "Cache-Control: "
        + cabecalho_seguro(
            resposta_js,
            "Cache-Control",
        )
    )

    if resposta_js.status_code != 200:
        linhas.append("")
        linhas.append(
            "O JavaScript não retornou HTTP 200."
        )

        ARQUIVO_RELATORIO.write_text(
            "\n".join(linhas),
            encoding="utf-8",
        )

        print(
            "Verificação encerrada. "
            "O arquivo não retornou HTTP 200."
        )
        return

    linhas.append(
        "SHA-256 do JavaScript: "
        + hash_completo(resposta_js.content)
    )

    texto_js = resposta_js.text

    possui_source_map = (
        "sourceMappingURL" in texto_js
    )

    linhas.append(
        "Referência a source map: "
        + ("SIM" if possui_source_map else "NÃO")
    )
    linhas.append("")
    linhas.append("3. CAMPOS LOCALIZADOS")
    linhas.append(
        "Os valores completos não foram registrados."
    )
    linhas.append("")

    resultados = localizar_campos(texto_js)

    for resultado in resultados:
        linhas.append(
            f"Campo: {resultado['campo']}"
        )
        linhas.append(
            "Encontrado: "
            + (
                "SIM"
                if resultado["encontrado"]
                else "NÃO"
            )
        )
        linhas.append(
            f"Ocorrências: {resultado['quantidade']}"
        )
        linhas.append(
            f"Tamanho: {resultado['tamanho']}"
        )
        linhas.append(
            f"SHA-256 parcial: {resultado['hash']}"
        )
        linhas.append(
            "Classificação: "
            + resultado["classificacao"]
        )
        linhas.append("-" * 40)

    linhas.append("")
    linhas.append("4. LIMITAÇÕES")
    linhas.append(
        "- Nenhuma credencial foi utilizada."
    )
    linhas.append(
        "- Nenhuma autenticação foi realizada."
    )
    linhas.append(
        "- Nenhum endpoint protegido foi testado."
    )
    linhas.append(
        "- Nenhum dado pessoal foi consultado."
    )
    linhas.append(
        "- O conteúdo bruto do JavaScript "
        "não foi salvo."
    )
    linhas.append(
        "- A existência dos campos não confirma "
        "acesso indevido."
    )

    ARQUIVO_RELATORIO.write_text(
        "\n".join(linhas),
        encoding="utf-8",
    )

    print("Confirmação passiva concluída!")
    print(f"Status do site: {resposta_site.status_code}")
    print(f"Status do JS: {resposta_js.status_code}")
    print(
        "JavaScript carregado pelo site:",
        javascript_carregado,
    )
    print(
        "Relatório salvo em:",
        ARQUIVO_RELATORIO,
    )


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as erro:
        print(
            "Erro de conexão durante "
            f"a verificação passiva: {erro}"
        )

    except Exception as erro:
        print(
            "Erro durante a análise: "
            f"{erro}"
        )