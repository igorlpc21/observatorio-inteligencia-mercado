# Observatório — Inteligência de Mercado

Projeto de inteligência competitiva criado para organizar informações públicas de distribuidores, avaliar a cobertura dos catálogos, medir a qualidade dos dados e identificar produtos potencialmente semelhantes entre empresas do mercado.

## 🌐 Observatório online

**Acesse a versão publicada:**

👉 https://igorlpc21.github.io/observatorio-inteligencia-mercado/

A versão web apresenta os principais indicadores do projeto, cobertura das bases, qualidade dos dados, distribuição das faixas de similaridade e uma bancada interativa para explorar pares de produtos candidatos à equivalência.

> **Importante:** similaridade textual indica um candidato à investigação. Ela não comprova equivalência comercial, técnica, regulatória ou de aplicação entre produtos.

---

## Objetivo do projeto

O Observatório foi desenvolvido para transformar dados públicos dispersos em uma estrutura comparável de inteligência de mercado.

A proposta não é definir qual empresa é melhor, mas criar critérios padronizados de observação que permitam:

* mapear a presença pública das empresas;
* organizar produtos, marcas e segmentos;
* medir cobertura e qualidade das informações;
* identificar sobreposição entre portfólios;
* gerar hipóteses para investigação comercial;
* apoiar análises de posicionamento;
* criar uma base evolutiva que possa receber novas fontes ao longo do tempo.

---

## Empresas observadas

O recorte atual contempla:

| Empresa               | Granularidade disponível | Uso analítico                       |
| --------------------- | ------------------------ | ----------------------------------- |
| Fortali Distribuidora | Produto                  | Variedade, nomes e embalagens       |
| Casa Garcia Gourmet   | Produto                  | Variedade, nomes e embalagens       |
| Milk Distribuidora    | Produto                  | Variedade, nomes e embalagens       |
| Safra Distribuidora   | Marca                    | Presença de marcas e segmentos      |
| WMix Ceará            | Segmento                 | Posicionamento público por segmento |

Nem todas as empresas disponibilizam o mesmo nível de detalhe.

Por isso, as análises respeitam a granularidade real de cada fonte e evitam comparar informações que não são equivalentes.

---

## O que o projeto entrega

O repositório reúne todo o ciclo analítico:

* coleta de informações públicas;
* armazenamento dos dados brutos;
* extração de informações;
* normalização de nomes, códigos e embalagens;
* auditoria de qualidade;
* tratamento de duplicidades;
* consolidação de catálogos;
* criação de indicadores;
* análise de similaridade de produtos;
* revisão exploratória dos candidatos;
* geração de gráficos;
* publicação do Observatório em ambiente web.

---

## Arquitetura do processo

```text
Fontes públicas
      ↓
Coleta e extração
      ↓
Armazenamento dos dados brutos
      ↓
Normalização
      ↓
Auditoria de qualidade
      ↓
Consolidação dos catálogos
      ↓
Padronização de quantidade e unidade
      ↓
Bloqueio de candidatos comparáveis
      ↓
Similaridade textual
      ↓
Revisão humana
      ↓
Indicadores e visualizações
      ↓
Observatório Web
```

---

## Estrutura do repositório

```text
.
├── dados/
│   ├── brutos/
│   │   └── materiais coletados sem transformação
│   │
│   ├── catalogos/
│   │   └── documentos e catálogos utilizados como fonte
│   │
│   └── tratados/
│       └── tabelas normalizadas, auditadas e consolidadas
│
├── docs/
│   └── documentação do processo e decisões metodológicas
│
├── graficos/
│   └── visualizações estáticas geradas durante a análise
│
├── relatorios/
│   └── relatórios e registros analíticos
│
├── site/
│   └── versão de desenvolvimento da interface
│
├── index.html
├── styles.css
├── app.js
│
├── *.py
│   └── scripts do pipeline analítico
│
├── requirements.txt
├── CONTRIBUTING.md
└── README.md
```

---

## Tecnologias utilizadas

### Coleta e tratamento

* Python
* Requests
* BeautifulSoup
* Expressões Regulares
* CSV
* Pandas

### Análise

* Python
* SequenceMatcher
* normalização textual
* tratamento de strings
* análise de similaridade
* auditoria de qualidade

### Visualização

* Matplotlib
* HTML
* CSS
* JavaScript

### Versionamento e publicação

* Git
* GitHub
* GitHub Pages
* Visual Studio Code

---

## Dados tratados utilizados pelo Observatório

A aplicação publicada utiliza principalmente:

```text
dados/tratados/indicadores_observatorio.csv
```

e:

```text
dados/tratados/comparacoes_candidatas_milk_fortali.csv
```

Esses arquivos alimentam os principais elementos do dashboard:

* registros observados;
* itens únicos;
* quantidade de catálogos em nível de produto;
* pares de alta similaridade;
* cobertura por empresa;
* qualidade dos catálogos;
* distribuição das faixas de similaridade;
* tabela de equivalências.

---

## Similaridade de produtos

O motor atual de similaridade compara produtos Milk × Fortali.

A lógica foi construída em etapas para reduzir falsos positivos.

### 1. Normalização

Antes da comparação, os nomes passam por padronização.

Entre os tratamentos estão:

* conversão de caixa;
* tratamento de acentos;
* remoção de pontuação;
* normalização de espaços;
* separação de medidas;
* padronização textual.

### 2. Bloqueio por embalagem

Produtos só entram no mesmo conjunto de candidatos quando possuem:

* mesma quantidade-base;
* mesma unidade-base.

Exemplo:

```text
1 KG × 1 KG
500 G × 500 G
1 L × 1 L
```

Isso evita comparar produtos com embalagens incompatíveis.

### 3. Similaridade textual

Depois do bloqueio, os nomes normalizados são comparados por proximidade textual.

A pontuação varia de:

```text
0 a 100
```

Quanto maior a pontuação, maior a proximidade entre os nomes.

---

## Faixas de similaridade

O Observatório utiliza as seguintes faixas de priorização:

| Faixa         |    Pontuação | Interpretação               |
| ------------- | -----------: | --------------------------- |
| Alta          |        ≥ 85% | Forte candidato à revisão   |
| Média         | 70% a 84,99% | Similaridade relevante      |
| Exploratória  | 55% a 69,99% | Candidato para investigação |
| Fora da lista |        < 55% | Similaridade insuficiente   |

Mesmo na faixa alta, o produto ainda precisa ser verificado quanto a:

* marca;
* sabor;
* composição;
* aplicação;
* categoria;
* unidade comercial;
* contexto do produto.

---

## Princípio de análise

O Observatório não foi construído como um ranking de empresas.

A proposta é observar cada empresa utilizando critérios consistentes e identificar oportunidades de melhoria dentro de sua própria realidade.

Exemplos de perguntas que o projeto busca responder:

* Qual empresa disponibiliza maior detalhamento público de catálogo?
* Onde existem lacunas de informação?
* Quais portfólios possuem maior sobreposição?
* Quais produtos merecem investigação manual?
* Quais empresas apresentam maior maturidade de dados públicos?
* Quais informações poderiam melhorar a descoberta dos produtos?
* Como a estrutura pública de cada empresa pode evoluir?

---

## Limitações atuais

Existem limitações importantes no recorte analisado.

### Preços

As fontes consolidadas não disponibilizaram preços públicos suficientes para uma comparação confiável.

Por isso, o projeto atualmente não compara:

* preço;
* margem;
* desconto;
* competitividade financeira;
* política comercial.

### Granularidade

Nem todas as empresas possuem catálogo público em nível de produto.

Algumas fontes permitem análise apenas de:

* marcas;
* categorias;
* segmentos;
* posicionamento institucional.

Essas diferenças são preservadas no modelo analítico.

### Similaridade

A similaridade textual não representa equivalência comercial automática.

O resultado é usado apenas para:

```text
priorizar investigação
```

e não para declarar que dois produtos são necessariamente substitutos.

---

## Qualidade dos dados

O projeto inclui etapas específicas de auditoria.

Entre os pontos avaliados estão:

* campos vazios;
* códigos inválidos;
* registros duplicados;
* consistência de medidas;
* padronização textual;
* granularidade da fonte;
* presença de informações relevantes.

Arquivos relacionados à auditoria podem ser encontrados em:

```text
dados/tratados/
```

---

## Executando localmente

Clone o repositório:

```powershell
git clone https://github.com/igorlpc21/observatorio-inteligencia-mercado.git
```

Entre na pasta:

```powershell
cd observatorio-inteligencia-mercado
```

Crie o ambiente virtual:

```powershell
python -m venv .venv
```

Ative:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Inicie um servidor local:

```powershell
python -m http.server 8000
```

Abra no navegador:

```text
http://localhost:8000/
```

Não abra o `index.html` diretamente com duplo clique, pois o JavaScript precisa carregar os arquivos CSV pelo servidor HTTP.

---

## Reproduzindo as principais etapas

Algumas das principais saídas podem ser reconstruídas utilizando:

```powershell
python reconstruir_catalogo_validado.py
python auditar_qualidade_catalogos.py
python encontrar_produtos_semelhantes.py
python gerar_indicadores_observatorio.py
```

Antes de executar coletores novamente, é importante verificar se a estrutura das páginas públicas permanece igual à utilizada originalmente.

---

## Atualização do Observatório

O projeto foi pensado para ser incremental.

Novas fontes podem ser adicionadas mantendo o mesmo fluxo:

```text
nova fonte
   ↓
coleta
   ↓
normalização
   ↓
validação
   ↓
integração ao catálogo
   ↓
novos indicadores
   ↓
atualização do Observatório
```

Isso permite aumentar gradualmente a cobertura do mercado sem reconstruir toda a solução.

---

## Uso responsável

O projeto trabalha exclusivamente com informações públicas dentro do recorte analisado.

Boas práticas adotadas:

* preservar a fonte original;
* registrar a origem das informações;
* manter datas de referência;
* evitar inferências além do que os dados permitem;
* diferenciar ausência de informação de ausência de operação;
* manter revisão humana;
* respeitar diferenças de granularidade;
* evitar exposição desnecessária de dados;
* revisar termos de uso e aspectos legais antes de redistribuir materiais coletados.

---

## Documentação

A documentação complementar está disponível em:

```text
docs/
```

Incluindo informações sobre:

* processo de coleta;
* metodologia;
* tratamento;
* decisões analíticas;
* versionamento;
* atualização do projeto.

---

## Contribuição

Orientações para evolução do projeto estão disponíveis em:

[`CONTRIBUTING.md`](CONTRIBUTING.md)

---

## Acesso ao projeto

### Observatório

🌐 https://igorlpc21.github.io/observatorio-inteligencia-mercado/

### Repositório

💻 https://github.com/igorlpc21/observatorio-inteligencia-mercado

---

## Status

**Versão atual:** agosto de 2026

O projeto permanece em evolução e pode receber novas empresas, fontes públicas, critérios de qualidade e métodos de análise conforme a disponibilidade dos dados.
