# Como contribuir

Este projeto trabalha com evidências públicas e transformações reproduzíveis. Toda contribuição deve preservar a rastreabilidade entre fonte, tratamento e resultado.

## Antes de começar

1. Leia [`README.md`](README.md) e [`docs/PROCESSO.md`](docs/PROCESSO.md).
2. Crie ou ative o ambiente virtual.
3. Instale `requirements.txt`.
4. Crie um branch descritivo.

```powershell
git switch -c tipo/descricao-curta
```

Exemplos:

- `dados/atualizar-casa-garcia`;
- `analise/revisar-similaridade`;
- `site/melhorar-acessibilidade`;
- `docs/explicar-taxonomia`.

## Atualização de dados

Uma atualização deve informar:

- empresa e fonte consultada;
- URL ou documento de origem;
- data e hora da coleta;
- escopo observado;
- script utilizado;
- quantidade de registros antes e depois;
- limitações ou erros encontrados.

Não apague o nome original do produto. Novas regras devem escrever em campos derivados ou gerar uma nova saída tratada.

## Validação mínima

Antes de propor uma mudança:

```powershell
python auditar_qualidade_catalogos.py
python gerar_indicadores_observatorio.py
node --check site/app.js
```

Também verifique o site em `http://127.0.0.1:8000/site/` nas larguras de desktop e celular.

## Commits

Prefira mensagens curtas, no imperativo, que expliquem o resultado:

```text
docs: documenta pipeline de similaridade
dados: atualiza catálogo Casa Garcia
site: amplia rótulos dos gráficos
fix: preserva zero à esquerda em códigos
```

Não inclua `.venv`, caches, segredos, credenciais ou arquivos temporários.

## Revisão analítica

Mudanças em métricas ou similaridade devem responder:

1. Qual decisão essa regra apoia?
2. Qual é a unidade e a granularidade?
3. A fonte é compatível com a comparação?
4. Como valores ausentes são tratados?
5. Quais falsos positivos e falsos negativos podem surgir?
6. A saída continua exigindo revisão humana?

