from datetime import datetime
from hashlib import sha256
from pathlib import Path
import re

import requests


URL_JS = (
    "https://mercadodosabor.com.br/"
    "static/js/main.1fab0e69.chunk.js"
)

ARQUIVO_SAIDA = (
    Path("relatorios")
    / "analise_uso_campos_redigida.txt"
)

CABECALHOS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "PassiveStaticAnalysis/1.0"
    )
}


PADROES = {
    "Auth-Token": (
        r'["\']Auth-Token["\']'
        r'\s*:\s*["\']([^"\']+)'
    ),
    "client_id": (
        r'client_id\s*:\s*'
        r'["\']([^"\']+)'
    ),
    "client_secret": (
        r'client_secret\s*:\s*'
        r'["\']([^"\']+)'
    ),
    "Firebase apiKey": (
        r'apiKey\s*:\s*'
        r'["\']([^"\']+)'
    ),
    "Chave fixa de criptografia": (
        r'(?:aes\.decrypt|decrypt)'
        r'\s*\([^,]+,\s*'
        r'["\']([^"\']+)'
    ),
}


def hash_parcial(valor):
    return sha256(
        valor.encode("utf-8")
    ).hexdigest()[:16]


def possui(contexto, termos):
    return any(
        termo.lower() in contexto
        for termo in termos
    )


def sim_nao(resultado):
    return "SIM" if resultado else "NÃO"


def analisar_contexto(contexto):
    contexto = contexto.lower()

    return {
        "http": possui(
            contexto,
            [
                "axios",
                "fetch(",
                ".post(",
                ".get(",
                "request(",
                "headers",
            ],
        ),
        "oauth": possui(
            contexto,
            [
                "oauth",
                "grant_type",
                "client_credentials",
                "authorization_code",
                "refresh_token",
                "access_token",
                "/token",
            ],
        ),
        "cabecalho": possui(
            contexto,
            [
                "headers",
                "authorization",
                "auth-token",
            ],
        ),
        "armazenamento": possui(
            contexto,
            [
                "localstorage",
                "sessionstorage",
            ],
        ),
        "criptografia": possui(
            contexto,
            [
                "aes",
                "decrypt",
                "encrypt",
                "crypto",
            ],
        ),
    }


def main():
    print(
        "Baixando uma cópia pública "
        "somente para análise em memória..."
    )

    resposta = requests.get(
        URL_JS,
        headers=CABECALHOS,
        timeout=30,
        allow_redirects=True,
    )

    print(
        f"Status do JavaScript: "
        f"{resposta.status_code}"
    )

    if resposta.status_code != 200:
        print(
            "O JavaScript não pôde ser analisado."
        )
        return

    texto = resposta.text

    linhas = [
        "ANÁLISE ESTÁTICA REDIGIDA",
        "=" * 60,
        f"Data: {datetime.now().astimezone().strftime('%d/%m/%Y %H:%M:%S %z')}",
        f"Fonte pública: {URL_JS}",
        "",
        (
            "Nenhum valor completo foi "
            "registrado neste relatório."
        ),
        (
            "Os indicadores representam "
            "proximidade no código e precisam "
            "de validação técnica."
        ),
        "",
    ]

    total = 0

    for campo, padrao in PADROES.items():
        correspondencias = list(
            re.finditer(
                padrao,
                texto,
                flags=re.IGNORECASE,
            )
        )

        for numero, correspondencia in enumerate(
            correspondencias,
            start=1,
        ):
            total += 1

            valor = correspondencia.group(1)

            inicio = max(
                0,
                correspondencia.start() - 1200,
            )

            final = min(
                len(texto),
                correspondencia.end() + 1200,
            )

            contexto = texto[inicio:final]

            indicadores = analisar_contexto(
                contexto
            )

            linhas.extend([
                f"Campo: {campo}",
                f"Ocorrência: {numero}",
                f"Tamanho: {len(valor)}",
                (
                    "SHA-256 parcial: "
                    f"{hash_parcial(valor)}"
                ),
                (
                    "Próximo de chamada HTTP: "
                    f"{sim_nao(indicadores['http'])}"
                ),
                (
                    "Próximo de fluxo OAuth: "
                    f"{sim_nao(indicadores['oauth'])}"
                ),
                (
                    "Próximo de cabeçalho: "
                    f"{sim_nao(indicadores['cabecalho'])}"
                ),
                (
                    "Próximo de armazenamento local: "
                    f"{sim_nao(indicadores['armazenamento'])}"
                ),
                (
                    "Próximo de função criptográfica: "
                    f"{sim_nao(indicadores['criptografia'])}"
                ),
                "-" * 45,
            ])

    linhas.extend([
        "",
        f"Total de ocorrências analisadas: {total}",
        "",
        "LIMITAÇÕES",
        (
            "- Nenhuma credencial foi utilizada."
        ),
        (
            "- Nenhuma requisição foi enviada "
            "para a API."
        ),
        (
            "- Nenhum contexto bruto foi salvo."
        ),
        (
            "- Proximidade no JavaScript não "
            "confirma utilização efetiva."
        ),
    ])

    ARQUIVO_SAIDA.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARQUIVO_SAIDA.write_text(
        "\n".join(linhas),
        encoding="utf-8-sig",
    )

    print("Análise estática concluída!")
    print(
        f"Ocorrências analisadas: {total}"
    )
    print(
        f"Relatório salvo em: {ARQUIVO_SAIDA}"
    )


if __name__ == "__main__":
    try:
        main()

    except requests.RequestException as erro:
        print(
            "Erro durante a consulta pública: "
            f"{erro}"
        )

    except Exception as erro:
        print(
            "Erro durante a análise estática: "
            f"{erro}"
        )