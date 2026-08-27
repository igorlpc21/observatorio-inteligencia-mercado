# Processo completo do Observatório

Este documento explica como o projeto transforma fontes públicas heterogêneas em evidência organizada para inteligência de mercado. Ele foi escrito para permitir auditoria, ensino e continuidade do trabalho.

## 1. Objetivo analítico

O observatório procura responder a quatro perguntas:

1. Quais empresas e portfólios estão visíveis nas fontes públicas observadas?
2. Qual é a cobertura e a qualidade dos dados disponíveis?
3. Quais produtos podem representar ofertas semelhantes entre concorrentes?
4. Quais conclusões são sustentadas pelos dados e quais ainda dependem de validação?

O objeto de comparação muda conforme a granularidade da fonte:

- **produto:** permite estudar nomes, variedade e embalagens;
- **marca:** permite estudar presença de fornecedores e segmentos;
- **segmento:** permite estudar posicionamento público;
- **preço:** indisponível no conjunto consolidado atual.

Granularidades diferentes são apresentadas juntas no panorama, mas não são tratadas como equivalentes no pareamento de produtos.

## 2. Fontes e aquisição

### Milk Distribuidora

Fonte principal: catálogo PDF datado de 14/02/2022.

Etapas associadas:

- `coletar_milk.py` obtém ou organiza o material de origem;
- `extrair_texto_catalogo_milk.py` transforma o PDF em texto pesquisável;
- `extrair_produtos_milk.py` identifica produtos e códigos;
- `extrair_grade_milk.py` extrai a estrutura de itens e embalagens;
- `normalizar_produtos_milk.py` padroniza campos;
- `consolidar_produtos_milk.py` reúne candidatos e revisões;
- `validar_chaves_milk.py` verifica chaves e duplicidades.

### Fortali Distribuidora

Fonte principal: páginas públicas do catálogo de confeitaria.

Etapas associadas:

- `coletar_catalogo_fortali.py` captura páginas do catálogo;
- `inspecionar_fortali.py` e `inspecionar_paginacao_fortali.py` verificam estrutura e paginação;
- `extrair_produtos_fortali.py` transforma o HTML em linhas de produto;
- `normalizar_produtos_fortali.py` padroniza nomes, códigos e medidas.

### Casa Garcia Gourmet

Fonte principal: páginas públicas de categorias e produtos.

Etapas associadas:

- `inspecionar_casa_garcia.py` verifica a estrutura da fonte;
- `coletar_casa_garcia.py` executa coleta inicial;
- `coletar_casa_garcia_completo.py` amplia a cobertura;
- `tratar_casa_garcia.py` limpa e estrutura os registros;
- `consolidar_casa_garcia.py` incorpora a fonte ao catálogo.

### Safra Distribuidora

A observação pública disponível foi consolidada em nível de marca, não de produto.

- `inspecionar_site_safra.py` examina a presença pública;
- `inspecionar_javascript_safra.py` verifica recursos carregados pelo site;
- `localizar_api_catalogo_safra.py` procura uma fonte estruturada pública;
- `testar_api_publica_safra.py` avalia a resposta encontrada;
- `coletar_fornecedores_safra.py` reúne fornecedores e marcas;
- `portfolio_marcas_safra.csv` representa a saída comparável atual.

### WMix Ceará

A fonte pública foi consolidada em nível de segmento:

- `criar_perfil_publico_wmix.py` organiza categorias e posicionamento observável;
- `perfil_publico_wmix.csv` é a saída utilizada no panorama.

## 3. Camadas de dados

### Dados brutos

Local: `dados/brutos/` e `dados/catalogos/`.

Essa camada preserva o material recebido ou coletado com o mínimo de alteração. Ela permite refazer uma extração quando as regras de tratamento evoluírem.

### Dados tratados

Local: `dados/tratados/`.

Essa camada contém tabelas estruturadas e saídas intermediárias. Os principais campos do catálogo mestre são:

| Campo | Significado |
| --- | --- |
| `id_registro` | identificador interno do registro |
| `empresa` | empresa associada à fonte |
| `departamento` | categoria ou departamento observado |
| `produto_original` | nome como aparece na fonte |
| `produto_normalizado` | nome padronizado para análise |
| `codigo_produto` | código publicado pela fonte |
| `codigo_valido` | resultado da validação estrutural do código |
| `quantidade_base` | quantidade convertida para uma base comum |
| `unidade_base` | unidade padronizada, como `G` ou `ML` |
| `status_validacao` | prontidão ou necessidade de revisão |
| `data_referencia` | data associada à observação |
| `fonte` | URL ou arquivo que sustenta o registro |

## 4. Normalização

A normalização busca tornar registros comparáveis sem apagar a evidência original.

Princípios:

1. O nome original é preservado.
2. Acentos, caixa e pontuação podem ser padronizados em campos derivados.
3. Medidas são separadas do nome.
4. Quilogramas e litros são convertidos para unidades-base quando aplicável.
5. Códigos são tratados como texto para preservar zeros à esquerda.
6. Valores ausentes permanecem ausentes; não são inventados.

## 5. Consolidação do catálogo mestre

`criar_catalogo_mestre_inicial.py` e `consolidar_casa_garcia.py` constroem versões progressivas do catálogo.

`reconstruir_catalogo_validado.py` substitui a versão anterior da Milk por registros validados e produz:

```text
dados/tratados/catalogo_mestre_validado.csv
```

O arquivo consolidado contém 4.997 registros em nível de produto:

- Fortali: 3.226;
- Casa Garcia: 1.627;
- Milk: 144.

Safra e WMix permanecem em tabelas próprias porque a granularidade pública disponível é diferente.

## 6. Auditoria de qualidade

`auditar_qualidade_catalogos.py` verifica, entre outros pontos:

- registros duplicados;
- chaves repetidas ou vazias;
- nomes ausentes;
- quantidade de categorias;
- preenchimento de peso ou volume;
- validade estrutural de códigos.

Saída principal:

```text
dados/tratados/auditoria_qualidade_catalogos.csv
```

A auditoria mede a qualidade do dado coletado, não a qualidade operacional da empresa analisada.

## 7. Similaridade de produtos

### 7.1 Preparação do nome

`encontrar_produtos_semelhantes.py`:

- converte o texto para caixa alta;
- remove acentos;
- remove medidas do nome, porque elas são verificadas separadamente;
- remove pontuação;
- reduz espaços repetidos.

### 7.2 Bloqueio por embalagem

Um produto Milk só é comparado com um produto Fortali quando ambos possuem:

```text
quantidade_base igual
e
unidade_base igual
```

Esse bloqueio reduz falsos positivos entre produtos com nomes parecidos, mas embalagens incompatíveis.

### 7.3 Pontuação textual

O projeto utiliza `difflib.SequenceMatcher`. A razão entre as duas sequências normalizadas é multiplicada por 100.

```text
similaridade = SequenceMatcher(nome_milk, nome_fortali).ratio() × 100
```

Somente candidatos com pelo menos 55% são mantidos. Para cada item Milk, são preservadas no máximo as três melhores opções da Fortali.

### 7.4 Classificação

| Faixa | Interpretação operacional |
| --- | --- |
| ≥ 85% | alta prioridade de revisão |
| 70% a 84,99% | prioridade média |
| 55% a 69,99% | candidato exploratório |
| < 55% | descartado pelo corte atual |

Saída:

```text
dados/tratados/comparacoes_candidatas_milk_fortali.csv
```

O resultado atual contém 54 pares candidatos, associados a 24 produtos Milk. Três pares atingem a faixa alta.

### 7.5 Por que revisão humana é obrigatória

O algoritmo não compreende integralmente:

- marca e fabricante;
- sabor ou variante;
- composição e ingredientes;
- uso culinário;
- unidade de venda versus conteúdo líquido;
- substituição técnica ou comercial.

Consequentemente, `equivalencia_confirmada` permanece negativa até uma validação explícita.

## 8. Indicadores e visualizações

`gerar_indicadores_observatorio.py` combina:

- catálogo mestre validado;
- portfólio de marcas Safra;
- perfil público WMix.

Ele produz `indicadores_observatorio.csv` e gráficos em `graficos/`.

Os indicadores usados no site incluem:

- registros observados;
- itens únicos;
- granularidade da fonte;
- categorias identificadas;
- taxa de medidas preenchidas;
- taxa de códigos válidos;
- presença de preços públicos;
- escopo comparável.

## 9. Site do observatório

O site estático fica em `site/`:

- `index.html`: conteúdo e estrutura semântica;
- `styles.css`: sistema visual principal;
- `readability.css`: camada de legibilidade e identidade;
- `app.js`: carregamento dos CSVs, filtros, tabela e SVGs;
- `assets/observatorio-mark.png`: símbolo visual do observatório.

O navegador faz a leitura dos CSVs por `fetch`. Por isso, o site deve ser servido por HTTP local.

## 10. Atualização recomendada

Para atualizar uma fonte:

1. registre a data e o endereço da observação;
2. preserve a versão bruta;
3. execute o extrator da fonte;
4. normalize os campos sem sobrescrever a evidência original;
5. rode a auditoria de qualidade;
6. reconstrua o catálogo mestre, se aplicável;
7. recalcule as similaridades;
8. regenere os indicadores;
9. abra o site e valide cartões, gráficos, filtros e tabela;
10. registre as mudanças em um branch Git próprio.

## 11. Limitações conhecidas

- As datas das fontes não são uniformes; o catálogo Milk é de 2022 e outras coletas são de 2026.
- O volume observado não representa participação de mercado.
- A ausência de preço público impede comparação comercial.
- O recorte Fortali começou em confeitaria e pode não representar todo o portfólio.
- Categorias dependem da taxonomia publicada por cada fonte.
- Similaridade textual não substitui uma taxonomia de produto nem validação técnica.
- Sites externos podem mudar e quebrar coletores.

## 12. Próximas evoluções

1. Criar taxonomia canônica de categorias, marcas, sabores e aplicações.
2. Separar marca, produto, variante e embalagem em campos próprios.
3. Adicionar testes automatizados para normalização e conversão de unidades.
4. Criar uma fila de revisão humana com decisão e justificativa.
5. Versionar snapshots por data de coleta.
6. Implementar indicadores de atualização e cobertura por fonte.
7. Adicionar novas empresas somente após definir granularidade e fonte de verdade.

