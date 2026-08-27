from pathlib import Path

import pandas as pd


pasta_dados = Path("dados")

estruturas = {
    "catalogo_mestre.csv": [
        "id_coleta",
        "empresa",
        "produto_original",
        "produto_padronizado",
        "marca",
        "categoria",
        "quantidade_embalagem",
        "unidade_medida",
        "preco",
        "preco_unitario_padronizado",
        "promocao",
        "disponibilidade",
        "url_fonte",
        "data_coleta"
    ],

    "cesta_benchmark.csv": [
        "id_item",
        "produto_padronizado",
        "marca_referencia",
        "quantidade_referencia",
        "unidade_referencia",
        "categoria",
        "prioridade"
    ],

    "cotacoes_logisticas.csv": [
        "id_cotacao",
        "empresa",
        "perfil_compra",
        "cidade_destino",
        "cep_destino",
        "valor_produtos",
        "desconto",
        "frete",
        "custo_total_entregue",
        "pedido_minimo",
        "prazo_dias",
        "retirada_loja",
        "data_cotacao",
        "fonte"
    ]
}

for nome_arquivo, colunas in estruturas.items():
    caminho = pasta_dados / nome_arquivo

    if caminho.exists():
        print(f"O arquivo já existe: {caminho}")
        continue

    tabela = pd.DataFrame(columns=colunas)

    tabela.to_csv(
        caminho,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"Arquivo criado: {caminho}")

print("\nModelo analítico criado com sucesso!")