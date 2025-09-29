# REST API de Dados Abertos (CNPq)

## Descrição do Projeto
Este projeto tem como objetivo principal a análise e a implementação de uma API RESTful para consulta de um conjunto de dados abertos do [Portal Brasileiro de Dados Abertos](https://dados.gov.br/dados/conjuntos-dados/bolsas-e-auxilios-pagos). A API é construída usando o framework **FastAPI** e utiliza **SQLAlchemy** para a modelagem do banco de dados.

O conjunto de dados selecionado é o de **Pagamentos do CNPq (jan–dez/2024)**, que registra bolsas e auxílios concedidos a pesquisadores, vinculados a instituições e programas de fomento à ciência e tecnologia.

## Conjunto de Dados
* **Origem:** Portal Dados.gov.br → CNPq
* **Nome do arquivo:** 20250204 Planilha Dados de Pagamento jan-dez_2024 - PDA CSV
* **Formato Original:** CSV
* **Periodicidade:** Anual (2024)
* **Total de Registros:** 219.662 linhas
* **Tamanho:** ~135 MB
* **Campos Principais:**
    * Ano de referência
    * Beneficiário (nome + CPF anonimizado)
    * Instituição (origem/destino)
    * Programa/Chamada
    * Modalidade e Linha de Fomento
    * Projeto vinculado
    * Valor pago

## Modelagem do Banco de Dados
A modelagem conceitual do banco de dados é baseada em 4 entidades principais, com seus respectivos relacionamentos:

* **Beneficiário:** `id`, `nome`, `cpf_anonimizado`, `categoria_nivel`
* **Instituição:** `id`, `nome`, `sigla`, `cidade`, `uf`, `pais`
* **Programa:** `id`, `nome_chamada`, `programa_cnpq`, `grande_area`, `area`, `subarea`
* **Pagamento:** `id`, `ano_referencia`, `processo`, `modalidade`, `linha_fomento`, `valor_pago`, `data_inicio`, `data_fim`, `titulo_projeto`, `fk_beneficiario` (FK), `fk_instituicao` (FK), `fk_programa` (FK)

### Relacionamentos
* Um **Beneficiário** pode receber vários **Pagamentos** (1:N).
* Uma **Instituição** pode estar vinculada a vários **Pagamentos** (1:N).
* Um **Programa** pode financiar vários **Pagamentos** (1:N).

Para uma representação visual do modelo de dados, consulte o Diagrama de Entidade-Relacionamento (DER) disponível em `documentacao/DER.pdf`.

## Estrutura da API
A aplicação é composta pelos seguintes módulos:
* `app/core/database.py`: Configuração da conexão com o banco de dados SQLite.
* `app/core/pagination.py`: Sistema de paginação avançada com ordenação.
* `app/core/filters.py`: Sistema de filtros dinâmicos para consultas.
* `app/core/security.py`: Autenticação JWT e segurança.
* `app/models/`: Definição dos modelos de dados (`Beneficiario`, `Instituicao`, `Pagamento`, `Programa`, `User`) usando SQLAlchemy.
* `app/schemas/`: Definição dos esquemas de dados para validação e serialização com Pydantic.
* `app/services/`: Lógica de negócio para interação com o banco de dados.
* `app/routers/`: Definição das rotas da API para cada entidade com funcionalidades avançadas.
* `app/main.py`: Ponto de entrada da aplicação FastAPI, onde as rotas são incluídas.

## Instalação e Execução

### Pré-requisitos
* Python 3.8+
* Git

### Passo a passo

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/itsnotgabxx/rest-api-dadosgov.git
    cd rest-api-dadosgov
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```
    * No Windows, use: `.venv\Scripts\activate`

3.  **Instale as dependências:**
    ```bash
    pip install "fastapi[standard]" python-jose[cryptography] passlib[bcrypt] python-multipart pandas
    ```

4.  **Baixe os dados do CNPq:**
    - Acesse: [Portal de Dados Abertos - CNPq](https://dados.gov.br/dados/conjuntos-dados/bolsas-e-auxilios-pagos)
    - Baixe o arquivo: "20250204 Planilha Dados de Pagamento jan-dez_2024 - PDA CSV"
    - Salve o arquivo CSV em uma pasta `dados/` na raiz do projeto
    - **Nota:** O arquivo tem ~135 MB e não está incluído no repositório

5.  **Popule o banco de dados:**
    ```bash
    # Criar diretório para os dados (se não existir)
    mkdir dados

    # Importar dados do CSV para o banco SQLite
    python import_cnpq_data.py dados/nome_do_arquivo.csv
    
    # Exemplo com nome real do arquivo:
    python import_cnpq_data.py "dados/20250204 Planilha Dados de Pagamento jan-dez_2024 - PDA CSV.csv"
    ```

    **Se não tiver o arquivo CSV:** O script criará dados de exemplo automaticamente:
    ```bash
    python import_cnpq_data.py
    ```

6.  **Crie um usuário administrador (opcional):**
    ```bash
    # Execute a aplicação primeiro para criar as tabelas
    uvicorn app.main:app --reload &

    # Em outro terminal, registre um admin via API
    curl -X POST "http://127.0.0.1:8000/auth/register" \
         -H "Content-Type: application/json" \
         -d '{
           "username": "admin",
           "email": "admin@exemplo.com",
           "password": "senha123",
           "role": "admin"
         }'
    ```

7.  **Execute a aplicação:**
    ```bash
    uvicorn app.main:app --reload
    ```

8.  **Acesse a documentação da API:**
    Abra seu navegador e acesse: `http://127.0.0.1:8000/docs`

## Utilização da API

### Autenticação
A API utiliza autenticação JWT. Primeiro, faça login para obter um token:

```bash
# Login
curl -X POST "http://127.0.0.1:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "admin",
       "password": "senha123"
     }'
```

Use o token retornado no header `Authorization: Bearer {token}` nas próximas requisições.

### Exemplos de Uso Avançado

```bash
# Listar instituições com paginação e filtros
curl -H "Authorization: Bearer {seu_token}" \
     "http://127.0.0.1:8000/instituicoes/?page=1&size=10&nome_like=federal&uf=SP&sort_by=nome"

# Buscar pagamentos por valor e ano
curl -H "Authorization: Bearer {seu_token}" \
     "http://127.0.0.1:8000/pagamentos/?ano_referencia=2024&valor_min=1000&valor_max=5000&sort_by=valor_pago&sort_order=desc"

# Busca geral em programas
curl -H "Authorization: Bearer {seu_token}" \
     "http://127.0.0.1:8000/programas/?search=produtividade&page=2&size=20"

# Estatísticas de pagamentos
curl -H "Authorization: Bearer {seu_token}" \
     "http://127.0.0.1:8000/pagamentos/stats"
```

## Rotas da API

### Autenticação (`/auth`)
* `POST /auth/register`: Registra um novo usuário
* `POST /auth/login`: Login do usuário
* `POST /auth/token`: Endpoint OAuth2 compatível
* `GET /auth/me`: Informações do usuário atual
* `GET /auth/users`: Lista usuários (apenas admin)

### Beneficiários (`/beneficiarios`)
* `GET /`: Lista beneficiários com **paginação, filtros e ordenação avançada**
  - Filtros: `search`, `nome`, `nome_like`, `categoria_nivel`, `cpf_anonimizado`
  - Paginação: `page`, `size`, `sort_by`, `sort_order`
* `GET /stats`: Estatísticas por categoria
* `GET /{beneficiario_id}`: Retorna um beneficiário por ID
* `POST /`: Cria um novo beneficiário (apenas admin)
* `PUT /{beneficiario_id}`: Atualiza um beneficiário (apenas admin)
* `DELETE /{beneficiario_id}`: Deleta um beneficiário (apenas admin)

### Instituições (`/instituicoes`)
* `GET /`: Lista instituições com **paginação, filtros e ordenação avançada**
  - Filtros: `search`, `nome`, `nome_like`, `sigla`, `cidade`, `cidade_like`, `uf`, `pais`
  - Paginação: `page`, `size`, `sort_by`, `sort_order`
* `GET /stats`: Estatísticas por UF e país
* `GET /{instituicao_id}`: Retorna uma instituição por ID
* `POST /`: Cria uma nova instituição (apenas admin)
* `PUT /{instituicao_id}`: Atualiza uma instituição (apenas admin)
* `DELETE /{instituicao_id}`: Deleta uma instituição (apenas admin)

### Programas (`/programas`)
* `GET /`: Lista programas com **paginação, filtros e ordenação avançada**
  - Filtros: `search`, `nome_chamada`, `nome_chamada_like`, `programa_cnpq`, `programa_cnpq_like`, `grande_area`, `area`, `subarea`
  - Paginação: `page`, `size`, `sort_by`, `sort_order`
* `GET /areas`: Estatísticas por áreas de conhecimento
* `GET /{programa_id}`: Retorna um programa por ID
* `POST /`: Cria um novo programa (apenas admin)
* `PUT /{programa_id}`: Atualiza um programa (apenas admin)
* `DELETE /{programa_id}`: Deleta um programa (apenas admin)

### Pagamentos (`/pagamentos`)
* `GET /`: Lista pagamentos com **paginação, filtros e ordenação avançada**
  - Filtros básicos: `search`, `ano_referencia`, `modalidade`, `linha_fomento`, `processo`, `titulo_projeto_like`
  - Filtros de valor: `valor_min`, `valor_max`
  - Filtros de data: `data_inicio_desde`, `data_inicio_ate`
  - Filtros por relacionamento: `beneficiario_id`, `instituicao_id`, `programa_id`
  - Paginação: `page`, `size`, `sort_by`, `sort_order`
* `GET /stats`: Estatísticas completas (totais, por modalidade, por ano)
* `GET /beneficiario/{beneficiario_id}`: Pagamentos por beneficiário (com paginação)
* `GET /instituicao/{instituicao_id}`: Pagamentos por instituição (com paginação)
* `GET /programa/{programa_id}`: Pagamentos por programa (com paginação)
* `GET /{pagamento_id}`: Retorna um pagamento por ID
* `POST /`: Cria um novo pagamento (apenas admin)
* `PUT /{pagamento_id}`: Atualiza um pagamento (apenas admin)
* `DELETE /{pagamento_id}`: Deleta um pagamento (apenas admin)

## Funcionalidades Avançadas

### Paginação e Ordenação
Todos os endpoints de listagem suportam:
- **Paginação**: `?page=2&size=20` (padrão: page=1, size=10, máximo: 100)
- **Ordenação**: `?sort_by=nome&sort_order=desc` (padrão: asc)
- **Metadados**: Retorna informações sobre total de itens, páginas, etc.

### Sistema de Filtros Dinâmicos
- **Busca geral**: `?search=universidade` (busca em todos os campos de texto)
- **Filtros exatos**: `?nome=valor_exato`
- **Filtros parciais**: `?nome_like=texto_parcial`
- **Filtros de range**: `?valor_min=1000&valor_max=5000`
- **Filtros de data**: `?data_inicio_desde=2024-01-01&data_inicio_ate=2024-06-30`
- **Filtros relacionais**: `?beneficiario_id=1&instituicao_id=2`

### Exemplos de Consultas Avançadas

```bash
# Instituições federais em São Paulo, ordenadas por nome
/instituicoes/?nome_like=federal&uf=SP&sort_by=nome&sort_order=asc

# Pagamentos de bolsas entre R$ 1.000 e R$ 10.000 em 2024
/pagamentos/?ano_referencia=2024&modalidade_like=bolsa&valor_min=1000&valor_max=10000

# Programas de Ciências Exatas, página 2 com 20 itens
/programas/?grande_area=Ciências Exatas&page=2&size=20&sort_by=nome_chamada

# Busca geral por "produtividade" em todos os campos
/programas/?search=produtividade

# Beneficiários categoria 1A, ordenados por nome decrescente
/beneficiarios/?categoria_nivel=1A&sort_by=nome&sort_order=desc
```

### Controle de Acesso
- **Leitor**: Pode consultar dados (todos os endpoints GET)
- **Admin**: Pode criar, atualizar e deletar dados (POST, PUT, DELETE)

### Estatísticas e Analytics
Endpoints especiais para análise de dados:
- `/beneficiarios/stats`: Distribuição por categoria
- `/instituicoes/stats`: Distribuição por UF e país
- `/programas/areas`: Distribuição por áreas de conhecimento
- `/pagamentos/stats`: Valores totais, médios, por modalidade e ano

## Estrutura de Arquivos

```
rest-api-dadosgov/
├── app/
│   ├── core/           # Configurações centrais
│   │   ├── config.py   # Configurações da aplicação
│   │   ├── database.py # Configuração do banco
│   │   ├── security.py # Autenticação JWT
│   │   ├── pagination.py # Sistema de paginação
│   │   ├── filters.py  # Sistema de filtros
│   │   └── deps.py     # Dependências compartilhadas
│   ├── models/         # Modelos SQLAlchemy
│   │   ├── beneficiario.py
│   │   ├── instituicao.py
│   │   ├── pagamento.py
│   │   ├── programa.py
│   │   └── user.py
│   ├── schemas/        # Esquemas Pydantic
│   │   ├── beneficiario.py
│   │   ├── instituicao.py
│   │   ├── pagamento.py
│   │   ├── programa.py
│   │   └── user.py
│   ├── services/       # Lógica de negócio
│   │   ├── beneficiario.py
│   │   ├── instituicao.py
│   │   ├── pagamento.py
│   │   ├── programa.py
│   │   └── user.py
│   ├── routers/        # Rotas da API (com funcionalidades avançadas)
│   │   ├── auth.py
│   │   ├── beneficiario.py
│   │   ├── instituicao.py
│   │   ├── pagamento.py
│   │   └── programa.py
│   └── main.py         # Aplicação principal
├── dados/              # Arquivos CSV (não versionados)
├── import_cnpq_data.py # Script de importação
├── sql_app.db          # Banco SQLite (criado automaticamente)
└── README.md
```

## Tecnologias Utilizadas
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para Python
- **SQLite**: Banco de dados embarcado
- **Pydantic**: Validação de dados
- **JWT**: Autenticação via tokens
- **Pandas**: Processamento de dados CSV
- **Uvicorn**: Servidor ASGI
- **Passlib + Bcrypt**: Hash de senhas seguro

## Performance e Escalabilidade
- **Paginação eficiente**: Limita resultados e melhora performance
- **Índices de banco**: Campos ID indexados automaticamente
- **Filtros otimizados**: Queries SQL eficientes com filtros dinâmicos
- **Serialização otimizada**: Conversão direta para JSON sem overhead
- **Cache de sessão**: Reutilização de conexões de banco

## Integrantes do Grupo
* Dimitri Monteiro – RGM: 29601380
* Gabrielly da Silva Oliveira – RGM: 30511640
* André Ruperto – RGM: 30003032
* Everman de Araújo – RGM: 30333717