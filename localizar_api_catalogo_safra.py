import re
from pathlib import Path


pasta_scripts = (
    Path("dados")
    / "brutos"
    / "javascript_safra"
)

arquivos_main = list(
    pasta_scripts.glob(
        "main.*.js"
    )
)

if not arquivos_main:
    print(
        "Arquivo main do JavaScript "
        "não encontrado."
    )

else:
    arquivo_main = arquivos_main[0]

    print(
        f"Analisando: {arquivo_main}"
    )

    conteudo = arquivo_main.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    conteudo = conteudo.replace(
        "\\/",
        "/"
    )

    termos = [
        "superstaging.merca",
        "comprasonline.merconnect.com.br",
        "brandId:875"
    ]

    linhas_resultado = []

    # Tenta localizar a definição direta.
    padroes_definicao = [
        r'mappURLV2\s*:\s*"([^"]+)"',
        r"mappURLV2\s*:\s*'([^']+)'",
        r'mappURLV2\s*=\s*"([^"]+)"',
        r"mappURLV2\s*=\s*'([^']+)'"
    ]

    print(
        "\n=== DEFINIÇÕES DIRETAS ==="
    )

    definicoes = []

    for padrao in padroes_definicao:
        resultados = re.findall(
            padrao,
            conteudo
        )

        definicoes.extend(
            resultados
        )

    definicoes = sorted(
        set(definicoes)
    )

    if definicoes:
        for definicao in definicoes:
            print(definicao)
            linhas_resultado.append(
                f"DEFINIÇÃO: {definicao}"
            )
    else:
        print(
            "Nenhuma definição direta "
            "foi encontrada."
        )

    print(
        "\n=== CONTEXTOS ENCONTRADOS ==="
    )

    for termo in termos:
        print(
            f"\n##### TERMO: {termo} #####"
        )

        inicio_busca = 0
        quantidade = 0

        while quantidade < 1:
            posicao = conteudo.find(
                termo,
                inicio_busca
            )

            if posicao == -1:
                break

            inicio = max(
                0,
                posicao - 500
            )

            fim = min(
                len(conteudo),
                posicao + 6000
            )

            trecho = (
                conteudo[inicio:fim]
                .replace("\n", " ")
            )

            print(
                f"\n--- OCORRÊNCIA "
                f"{quantidade + 1} ---"
            )

            print(trecho)

            linhas_resultado.append(
                f"\nTERMO: {termo}\n"
                f"{trecho}\n"
            )

            inicio_busca = (
                posicao
                + len(termo)
            )

            quantidade += 1

        if quantidade == 0:
            print(
                "Nenhuma ocorrência."
            )

    caminho_resultado = (
        Path("dados")
        / "brutos"
        / "resultado_api_safra.txt"
    )

    caminho_resultado.write_text(
        "\n".join(
            linhas_resultado
        ),
        encoding="utf-8"
    )

    print(
        f"\nResultado salvo em: "
        f"{caminho_resultado}"
    )