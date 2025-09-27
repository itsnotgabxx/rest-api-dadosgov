# REST API de Dados Abertos (CNPq)

## Descrição do Projeto
Este projeto tem como objetivo principal a análise e a implementação de uma API RESTful para consulta de um conjunto de dados abertos do [Portal Brasileiro de Dados Abertos](https://dados.gov.br/dados/conjuntos-dados/bolsas-e-auxilios-pagos). A API é construída usando o framework **FastAPI** e utiliza **SQLAlchemy** para a modelagem do banco de dados.

O conjunto de dados selecionado é o de **Pagamentos do CNPq (jan–dez/2024)**, que registra bolsas e auxílios concedidos a pesquisadores, vinculados a instituições e programas de fomento à ciência e tecnologia.

## Conjunto de Dados
* **Origem:** Portal Dados.gov.br → CNPq
* **Nome do arquivo:** 20250204 Planilha Dados de Pagamento jan-dez_2024 - PDA CSV
* **Formato Original:** CSV
* **Periodicidade:** Anual (2024)
* **Total de Registros:** Aproximadamente 219 mil linhas
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
* `app/models/`: Definição dos modelos de dados (`Beneficiario`, `Instituicao`, `Pagamento`, `Programa`) usando SQLAlchemy.
* `app/schemas/`: Definição dos esquemas de dados para validação e serialização com Pydantic.
* `app/services/`: Lógica de negócio para interação com o banco de dados.
* `app/routers/`: Definição das rotas da API para cada entidade.
* `app/main.py`: Ponto de entrada da aplicação FastAPI, onde as rotas são incluídas.

## Instalação e Execução
### Pré-requisitos
* Python 3.x

### Passo a passo
1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/itsnotgabxx/rest-api-dadosgov.git](https://github.com/itsnotgabxx/rest-api-dadosgov.git)
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
    pip install "fastapi[standard]"
    ```

4.  **Execute a aplicação com o uvicorn:**
    ```bash
    uvicorn app.main:app --reload
    ```

5.  **Acesse a documentação da API:**
    Abra seu navegador e acesse a URL: `http://127.0.0.1:8000/docs` para visualizar a documentação interativa da API, gerada automaticamente pelo Swagger UI.

## Rotas da API
A API expõe os seguintes endpoints:

* **Beneficiários (`/beneficiarios`)**
    * `POST /`: Cria um novo beneficiário.
    * `GET /{beneficiario_id}`: Retorna um beneficiário por ID.

* **Instituições (`/instituicoes`)**
    * `POST /`: Cria uma nova instituição.
    * `GET /{instituicao_id}`: Retorna uma instituição por ID.
    * `GET /`: Retorna uma lista de todas as instituições.

* **Pagamentos (`/pagamentos`)**
    * `POST /`: Cria um novo pagamento.
    * `GET /{pagamento_id}`: Retorna um pagamento por ID.
    * `GET /`: Retorna uma lista de todos os pagamentos.

* **Programas (`/programas`)**
    * `POST /`: Cria um novo programa.
    * `GET /{programa_id}`: Retorna um programa por ID.
    * `GET /`: Retorna uma lista de todos os programas.

## Integrantes do Grupo
* Dimitri Monteiro – RGM: 29601380
* Gabrielly da Silva Oliveira – RGM: 30511640
* André Ruperto – RGM: 30003032
* Everman de Araújo – RGM: 30333717
