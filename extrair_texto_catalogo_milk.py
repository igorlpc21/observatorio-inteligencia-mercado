from pathlib import Path

import pdfplumber


caminho_pdf = (
    Path("dados")
    / "catalogos"
    / "catalogo_milk_2022.pdf"
)

pasta_brutos = Path("dados") / "brutos"

pasta_brutos.mkdir(
    exist_ok=True
)

caminho_saida = (
    pasta_brutos
    / "catalogo_milk_2022.txt"
)

partes_texto = []
total_codigos = 0

with pdfplumber.open(caminho_pdf) as pdf:
    total_paginas = len(pdf.pages)

    for numero_pagina, pagina in enumerate(
        pdf.pages,
        start=1
    ):
        texto = pagina.extract_text(
            x_tolerance=2,
            y_tolerance=3
        )

        if not texto:
            texto = ""

        quantidade_codigos = (
            texto.lower().count("cód")
        )

        total_codigos += quantidade_codigos

        partes_texto.append(
            f"\n--- PÁGINA {numero_pagina} ---\n"
        )

        partes_texto.append(texto)

        print(
            f"Página {numero_pagina}: "
            f"{quantidade_codigos} códigos"
        )

texto_completo = "\n".join(partes_texto)

caminho_saida.write_text(
    texto_completo,
    encoding="utf-8"
)

print("\nExtração concluída!")
print(f"Quantidade de páginas: {total_paginas}")
print(f"Ocorrências de código: {total_codigos}")
print(f"Texto salvo em: {caminho_saida}")