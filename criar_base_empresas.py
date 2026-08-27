import pandas as pd
from pathlib import Path

empresas = [
    {
        "id_empresa": 1,
        "empresa": "Safra Distribuidora",
        "cidade_base": "Maracanaú",
        "estado": "CE",
        "site": "https://mercadodosabor.com.br/",
        "instagram": "https://www.instagram.com/distribuidorasafra/",
        "segmentos": "Confeitaria; Panificação; Sorveteria; Food Service"
    },
    {
        "id_empresa": 2,
        "empresa": "Fortali Distribuidora",
        "cidade_base": "Fortaleza",
        "estado": "CE",
        "site": "https://www.fortali.com.br/",
        "instagram": "https://www.instagram.com/fortali/",
        "segmentos": "Food Service; Confeitaria; Panificação; Sorveteria"
    },
    {
        "id_empresa": 3,
        "empresa": "Casa Garcia Gourmet",
        "cidade_base": "Fortaleza",
        "estado": "CE",
        "site": "https://casagarciafortaleza.com.br/",
        "instagram": "https://www.instagram.com/casagarciagourmet/",
        "segmentos": "Confeitaria; Panificação; Sorveteria; Embalagens"
    },
    {
        "id_empresa": 4,
        "empresa": "WMix Ceará",
        "cidade_base": "Fortaleza",
        "estado": "CE",
        "site": "",
        "instagram": "https://www.instagram.com/wmix_ceara/",
        "segmentos": "Confeitaria; Sorveteria; Açaiteria; Equipamentos"
    },
    {
        "id_empresa": 5,
        "empresa": "Milk Distribuidora",
        "cidade_base": "Eusébio",
        "estado": "CE",
        "site": "https://milkdistribuidora.com.br/",
        "instagram": "https://www.instagram.com/milkdistribuidora/",
        "segmentos": "Sorveteria; Confeitaria; Panificação"
    },
    {
        "id_empresa": 6,
        "empresa": "Distribuidora Sol Food Service",
        "cidade_base": "Fortaleza",
        "estado": "CE",
        "site": "",
        "instagram": "https://www.instagram.com/distribuidorasolfoodservice/",
        "segmentos": "Sorveteria; Açaiteria; Panificação; Confeitaria"
    }
]

df_empresas = pd.DataFrame(empresas)

caminho_arquivo = Path("dados") / "empresas.csv"

df_empresas.to_csv(
    caminho_arquivo,
    index=False,
    encoding="utf-8-sig"
)

print("Base de empresas criada com sucesso!")
print(f"Arquivo salvo em: {caminho_arquivo}")

print("\nEmpresas cadastradas:")
print(
    df_empresas[
        ["id_empresa", "empresa", "cidade_base"]
    ].to_string(index=False)
)