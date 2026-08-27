# Guia Git do projeto

O repositório local usa `main` como branch principal. Código, documentação, dados brutos, dados tratados, relatórios, gráficos e site fazem parte do snapshot reproduzível.

O ambiente virtual, caches, segredos e temporários não são versionados.

## Primeiro commit

Antes do primeiro commit, configure sua identidade Git:

```powershell
git config user.name "Seu Nome"
git config user.email "seu-email@exemplo.com"
```

Revise o snapshot preparado:

```powershell
git status
git diff --cached --stat
```

Crie o primeiro marco do projeto:

```powershell
git commit -m "chore: inicia observatório de inteligência de mercado"
```

## Rotina de trabalho

Atualize a branch principal e crie uma branch temática:

```powershell
git switch main
git switch -c dados/atualizar-fonte
```

Depois da alteração:

```powershell
git status
git diff
git add caminho/do/arquivo
git commit -m "dados: atualiza catálogo da empresa"
```

Prefira adicionar caminhos específicos durante o trabalho cotidiano. Isso facilita revisar o que será registrado.

## Publicar em um repositório remoto

Crie primeiro um repositório privado vazio no provedor escolhido. Não adicione README remoto, pois este projeto já possui documentação local.

Em seguida:

```powershell
git remote add origin URL_DO_REPOSITORIO
git push -u origin main
```

Antes de publicar, confirme:

- autorização para redistribuir o catálogo PDF e materiais coletados;
- ausência de credenciais e dados pessoais;
- decisão sobre licença;
- necessidade de manter o repositório privado;
- política de atualização dos snapshots.

## Arquivos grandes

O catálogo PDF da Milk possui aproximadamente 18 MB e pode ser versionado diretamente nos limites usuais do GitHub. Se documentos ou imagens crescerem significativamente, avalie Git LFS antes de adicioná-los ao histórico.

## Recuperar o projeto

Depois de clonar:

```powershell
git clone URL_DO_REPOSITORIO
cd inteligencia_competitiva_safra
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m http.server 8000
```

O observatório estará disponível em `http://127.0.0.1:8000/site/`.

