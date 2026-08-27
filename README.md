# Observatório — Inteligência de Mercado

Projeto de inteligência competitiva para organizar informações públicas de distribuidores, medir a cobertura dos catálogos e identificar produtos potencialmente semelhantes.

O repositório reúne todo o ciclo analítico: coleta, extração, normalização, auditoria de qualidade, consolidação, pareamento de produtos e apresentação dos resultados em um site interativo.

> **Importante:** similaridade textual indica um candidato à investigação. Ela não comprova equivalência comercial, técnica ou regulatória entre produtos.

## O que o projeto entrega

- catálogo mestre com registros de Milk, Fortali e Casa Garcia;
- perfis públicos de Safra e WMix em granularidade de marca ou segmento;
- auditorias de completude, duplicidade e validade de códigos;
- candidatos de similaridade entre produtos Milk e Fortali;
- indicadores consolidados do observatório;
- gráficos estáticos para análise auxiliar;
- site responsivo com filtros, métricas e tabela de equivalências.

## Visão atual dos dados

| Empresa | Granularidade | Registros observados | Uso analítico principal |
| --- | --- | ---: | --- |
| Fortali Distribuidora | Produto | 3.226 | Variedade, nomes e embalagens |
| Casa Garcia Gourmet | Produto | 1.627 | Variedade, nomes e embalagens |
| Milk Distribuidora | Produto | 144 | Variedade, nomes e embalagens |
| Safra Distribuidora | Marca | 31 | Presença de marcas e segmentos |
| WMix Ceará | Segmento | 5 | Posicionamento público por segmento |

No recorte atual, nenhuma das fontes consolidadas disponibiliza preços públicos. Por isso, o observatório não apresenta comparação de preço, margem ou competitividade comercial.

## Site do observatório

O site está em [`site/`](site/) e lê diretamente os arquivos tratados:

- `dados/tratados/indicadores_observatorio.csv`;
- `dados/tratados/comparacoes_candidatas_milk_fortali.csv`.

Para executar localmente:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m http.server 8000
```

Depois, acesse:

```text
http://127.0.0.1:8000/site/
```

Não abra o `index.html` diretamente com duplo clique. O navegador precisa do servidor local para carregar os CSVs.

## Estrutura do repositório

```text
.
├── dados/
│   ├── brutos/       # respostas, HTML e materiais como foram coletados
│   ├── catalogos/    # documentos-fonte, como o catálogo PDF da Milk
│   └── tratados/     # tabelas normalizadas, auditadas e consolidadas
├── docs/             # processo, decisões e documentação analítica
├── graficos/         # figuras estáticas geradas por Python
├── relatorios/       # relatórios e registros de análise
├── site/             # aplicação web estática do observatório
├── *.py              # etapas reproduzíveis do pipeline
└── requirements.txt  # dependências Python
```

## Processo resumido

```text
Fontes públicas
      ↓
Coleta e extração
      ↓
Normalização de nomes, códigos e embalagens
      ↓
Validação e auditoria de qualidade
      ↓
Catálogo mestre e perfis públicos
      ↓
Bloqueio por quantidade e unidade
      ↓
Similaridade textual e revisão humana
      ↓
Indicadores, gráficos e site
```

A explicação completa, com scripts, entradas, saídas e limitações, está em [`docs/PROCESSO.md`](docs/PROCESSO.md).

O procedimento para criar versões, branches e publicar o repositório está em [`docs/GIT.md`](docs/GIT.md).

## Similaridade de produtos

O pareamento atual compara Milk × Fortali em duas etapas:

1. **Bloqueio de embalagem:** somente itens com a mesma `quantidade_base` e `unidade_base` podem ser comparados.
2. **Proximidade textual:** os nomes são normalizados e comparados com `SequenceMatcher`.

Faixas de priorização:

- alta: pelo menos 85%;
- média: de 70% a 84,99%;
- exploratória: de 55% a 69,99%;
- abaixo de 55%: não entra na lista de candidatos.

Mesmo na faixa alta, os pares precisam ser verificados quanto a marca, sabor, aplicação, formulação e unidade comercial.

## Reproduzir as principais saídas

Os scripts foram mantidos como etapas independentes. A ordem exata depende da fonte que será atualizada, mas o fluxo consolidado é:

```powershell
python reconstruir_catalogo_validado.py
python auditar_qualidade_catalogos.py
python encontrar_produtos_semelhantes.py
python gerar_indicadores_observatorio.py
```

Consulte o processo completo antes de executar coletores, pois eles acessam páginas externas e podem depender da estrutura atual de cada site.

## Qualidade e uso responsável

- Preserve o arquivo bruto antes de qualquer transformação.
- Registre a data de referência e a URL da fonte.
- Não compare métricas com granularidades diferentes como se fossem equivalentes.
- Não interprete ausência de dado público como ausência de produto, preço ou operação.
- Mantenha a revisão humana dos pares de similaridade.
- Revise termos de uso, direitos autorais e requisitos legais antes de redistribuir materiais coletados.

## Contribuição

As orientações para atualizar fontes, validar saídas e propor mudanças estão em [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licença e acesso

Nenhuma licença de redistribuição foi definida. Até que o responsável pelo projeto escolha uma licença e revise os direitos sobre as fontes coletadas, trate este repositório e seus dados como material de uso interno.
