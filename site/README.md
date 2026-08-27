# Radar Safra

Site estático para apresentação dos resultados de inteligência competitiva.

## Executar

Na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe -m http.server 8000
```

Acesse `http://localhost:8000/site/`.

O site lê diretamente os CSVs tratados, sem dependências externas:

- `dados/tratados/indicadores_observatorio.csv`
- `dados/tratados/comparacoes_candidatas_milk_fortali.csv`

## Escopo analítico

O pareamento atual é Milk × Fortali. Primeiro exige mesma quantidade e unidade; depois calcula similaridade textual entre nomes normalizados. Os resultados são candidatos e exigem revisão humana.
