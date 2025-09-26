from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import beneficiario, instituicao, programa, pagamento, auth

# Importar modelo User para criar tabela
from app.models.user import User

# Criar todas as tabelas (incluindo users)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API CNPq - Dados Abertos",
    description="API REST para consulta de dados de pagamentos do CNPq com autenticação JWT",
    version="1.0.0"
)

# Incluir TODOS os routers
app.include_router(auth.router)           # ← ESTAVA FALTANDO
app.include_router(beneficiario.router)
app.include_router(instituicao.router) 
app.include_router(programa.router)
app.include_router(pagamento.router)

@app.get("/")
def read_root():
    return {
        "message": "API CNPq - Dados Abertos",
        "version": "1.0.0",
        "docs": "/docs",
        "auth": "JWT Bearer Token required for protected endpoints"
    }