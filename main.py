from datetime import datetime

empresas_analisadas = [
    "Safra Distribuidora",
    "Fortali Distribuidora",
    "Casa Garcia Gourmet",
    "WMix Ceará",
    "Milk Distribuidora",
    "Distribuidora Sol Food Service"
]

criterios_analise = [
    "Presença digital",
    "Variedade de produtos",
    "Promoções e preços",
    "Reputação dos clientes",
    "Cobertura geográfica",
    "Canais de atendimento",
    "Conteúdo técnico",
    "Diferenciais competitivos"
]

print("PROJETO DE INTELIGÊNCIA COMPETITIVA")
print(f"Data da execução: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

print("\nEmpresas analisadas:")

for numero, empresa in enumerate(empresas_analisadas, start=1):
    print(f"{numero}. {empresa}")

print("\nCritérios da análise:")

for numero, criterio in enumerate(criterios_analise, start=1):
    print(f"{numero}. {criterio}")