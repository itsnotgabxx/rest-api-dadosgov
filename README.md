## 👨‍🎓 Integrantes
- Dimitri Monteiro – RGM: 29601380
- Gabrielly da Silva Oliveira – RGM: 30511640
- André Ruperto – RGM: 30003032
- Everman de Araújo – RGM: 30333717

---

## COMO RODAR A APLICAÇÃO (DEDE E SEMPREHOMEM)

após clonar o repoisitório, abrir um novo terminal

rodar o comando 

 - python --version 

se não funcionar, rodar o comando 

- python3 --version

após verificar se o python está instalado

rodar o comando: 

 - python3 (ou python, depende da resposta dos comandos acima) -m venv .venv

após ter criado a pasta .venv, rodar o comando 

- source .venv/bin/activate

após isso, no seu terminal, antes do seu nome de usuário e pc, é para aparecer um .venv na frente, por exemplo:

(.venv) dimi@dimi:~/Documentos/rest-api-dadosgov$ 

se isso aconteceu, rode o comando

 - pip install fastapi[standard]

pronto, o ambiente está preparado!

--

## 📌 Introdução
Este trabalho tem como objetivo realizar a **análise de um conjunto de dados aberto**, disponível no [Portal Brasileiro de Dados Abertos](https://dados.gov.br), e a partir dele desenvolver a **modelagem conceitual** e a **implementação em banco de dados**.

O dataset escolhido foi o de **Pagamentos do CNPq (jan–dez/2024)**, que contém registros de bolsas e auxílios concedidos a pesquisadores, vinculados a instituições e programas de fomento à ciência e tecnologia.

---

## 📊 Conjunto de Dados
- **Origem:** Portal Dados.gov.br → CNPq  
- **Formato:** CSV  
- **Periodicidade:** anual (2024)  
- **Total de registros:** ~219 mil linhas  
- **Campos principais:**
  - Ano de referência  
  - Beneficiário (nome + CPF anonimizado)  
  - Instituição (origem/destino)  
  - Programa/Chamada  
  - Modalidade e Linha de Fomento  
  - Projeto vinculado  
  - Valor pago  

---

## 🗄️ Modelagem do Banco de Dados
Com base nos dados analisados, foi definida uma modelagem com **4 entidades principais**:

1. **Beneficiário**
   - id (PK)  
   - nome  
   - cpf_anonimizado  
   - categoria_nivel  

2. **Instituição**
   - id (PK)  
   - nome  
   - sigla  
   - cidade  
   - uf  
   - pais  

3. **Pagamento**
   - id (PK)  
   - ano_referencia  
   - processo  
   - modalidade  
   - linha_fomento  
   - valor_pago  
   - data_inicio  
   - data_fim  
   - titulo_projeto  
   - fk_beneficiario (FK)  
   - fk_instituicao (FK)  
   - fk_programa (FK)  

4. **Programa**
   - id (PK)  
   - nome_chamada  
   - programa_cnpq  
   - grande_area  
   - area  
   - subarea  

---

## 🔗 Relacionamentos
- **Beneficiário (1:N) Pagamento** → um beneficiário pode receber vários pagamentos.  
- **Instituição (1:N) Pagamento** → uma instituição pode estar vinculada a vários pagamentos.  
- **Programa (1:N) Pagamento** → um programa pode financiar vários pagamentos.  

<img width="1334" height="845" alt="image" src="https://github.com/user-attachments/assets/17d2d405-1ab5-4602-ac95-5c5bbadbe14d" />


---
