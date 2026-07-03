# Sistema de Controle de Estoque

Uma aplicação fullstack para gerenciamento de estoque, construída com Django REST Framework no backend e React no frontend. O projeto nasceu com foco em boas práticas: separação clara de responsabilidades, regras de negócio no modelo, transações atômicas e uma API versionada desde o primeiro commit.

---

## O que o sistema faz

- Cadastro de **produtos**, **categorias** e **fornecedores**
- Registro de **entradas e saídas** de estoque com rastreabilidade completa
- **Alertas automáticos** quando um produto cai abaixo do estoque mínimo ou zera
- Controle de **usuários por perfil** (Administrador e Operador)
- API REST com **autenticação JWT** e versionamento desde o início (`/api/v1/`)

---

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12 + Django + Django REST Framework |
| Frontend | React 18 + Vite + Bootstrap 5 + React Router |
| Banco de dados | PostgreSQL 16 |
| Autenticação | JWT via `djangorestframework-simplejwt` |
| Containerização | Docker (multi-stage build) + Docker Compose |

---

## Arquitetura

### Backend

O backend segue o padrão **Fat Model / Thin View**: a lógica de negócio vive nos models, não nas views. Isso torna o código mais testável e evita que as views acumulem responsabilidades que não são delas.

O exemplo mais claro é o model de `Movimentacao`. Toda vez que uma entrada ou saída é registrada, o sistema:

1. Valida que a quantidade é positiva
2. Valida que uma saída não vai gerar saldo negativo
3. Persiste a movimentação e atualiza o saldo do produto num único bloco atômico

```python
# O saldo é atualizado via F() expression — seguro para múltiplos workers
produto.objects.filter(pk=id).update(
    quantidade_atual=F("quantidade_atual") + quantidade
)
```

Movimentações são **imutáveis por design**: uma vez registrada, não pode ser editada. Para corrigir um lançamento errado, registra-se uma nova movimentação. Isso garante rastreabilidade total do histórico.

### Produtos

Cada produto carrega três propriedades de status de estoque:

- `normal` — quantidade acima do mínimo
- `abaixo_minimo` — quantidade positiva, mas abaixo do limite configurado
- `sem_estoque` — zerado

O valor monetário total em estoque (`quantidade × preço`) é calculado via `@property`, sem campo redundante no banco.

### Usuários

O modelo de usuário estende o `AbstractUser` do Django adicionando um campo `perfil` com dois níveis:

- **Administrador** — acesso total ao sistema
- **Operador** — pode registrar movimentações e consultar produtos, mas não acessa configurações nem pode excluir registros

A decisão de usar `AbstractUser` em vez do `User` padrão do Django evita dores de cabeça: uma vez que o projeto começa com o `User` padrão, trocar depois exige uma migration destrutiva.

### Frontend

O frontend é uma SPA em React consumindo a API. O build é feito com Vite e o resultado final é copiado para dentro da imagem Docker do Django via multi-stage build — o Node.js não vai para produção, apenas os arquivos estáticos compilados.

### Docker

O `Dockerfile` usa dois estágios:

```
Stage 1 (node:20-alpine)  → compila o React, gera /dist
Stage 2 (python:3.12-slim) → copia o /dist, roda o Django com Gunicorn
```

Isso mantém a imagem final enxuta: sem Node, sem source do frontend.

---

## Endpoints da API

```
POST   /api/v1/auth/token/           → login (retorna access + refresh)
POST   /api/v1/auth/token/refresh/   → renovar access token

GET    /api/v1/produtos/             → listar produtos
POST   /api/v1/produtos/             → cadastrar produto
GET    /api/v1/produtos/{id}/        → detalhe do produto
PUT    /api/v1/produtos/{id}/        → atualizar produto
DELETE /api/v1/produtos/{id}/        → remover produto
GET    /api/v1/produtos/abaixo_do_minimo/ → produtos em alerta
GET    /api/v1/produtos/sem_estoque/      → produtos zerados

GET    /api/v1/categorias/           → listar categorias
GET    /api/v1/fornecedores/         → listar fornecedores
POST   /api/v1/movimentacoes/        → registrar entrada ou saída
GET    /api/v1/movimentacoes/        → histórico de movimentações
GET    /api/v1/usuarios/             → listar usuários (admin only)
```

Filtros disponíveis em `/produtos/`:
- `?ativo=true`
- `?categoria=1`
- `?fornecedor=2`
- `?search=notebook`
- `?ordering=nome`

---

## Como rodar

### Com Docker (recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/Ricardorcunha/sistema-controle-estoque.git
cd sistema-controle-estoque

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 3. Suba os containers
docker compose up --build
```

O Docker Compose vai subir o PostgreSQL, rodar as migrations, criar um superusuário padrão e iniciar o Django com Gunicorn.

Acesse em: `http://localhost:8000`

Credenciais padrão: `admin` / `admin123` *(troque em produção)*

### Sem Docker

```bash
# Backend
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

pip install -r requirements/development.txt
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev
```

---

## Estrutura do projeto

```
├── apps/
│   ├── api/              # Permissões e configurações globais da API
│   ├── categorias/       # Modelo e ViewSet de Categoria
│   ├── fornecedores/     # Modelo e ViewSet de Fornecedor
│   ├── produtos/         # Modelo central — inclui status de estoque
│   ├── movimentacoes/    # Entradas e saídas — coração do sistema
│   └── usuarios/         # Usuário customizado com perfis
├── config/
│   └── settings/         # Settings separados por ambiente
├── frontend/             # React + Vite
├── tests/                # Testes automatizados
├── docker-compose.yml
└── Dockerfile
```

---

## Decisões técnicas que vale destacar

**`DecimalField` para preço, não `FloatField`**
`FloatField` tem imprecisão inerente em operações de ponto flutuante. `DecimalField` é exato — obrigatório para qualquer campo monetário.

**`on_delete=PROTECT` nas FKs**
Impede excluir uma categoria ou fornecedor que ainda tem produtos vinculados. Evita dados órfãos sem precisar de verificação manual.

**`F()` expression na atualização de saldo**
A atualização do estoque acontece diretamente no SQL (`UPDATE ... SET quantidade = quantidade + X`), o que é seguro em ambientes com múltiplos workers simultâneos. Ler o valor em Python e somar depois cria uma race condition.

**Versionamento de API desde o início**
Todos os endpoints vivem em `/api/v1/`. Quando mudanças incompatíveis forem necessárias, uma `/api/v2/` pode coexistir sem quebrar clientes já integrados.

---

## Autor

Ricardo — [github.com/Ricardorcunha](https://github.com/Ricardorcunha)
