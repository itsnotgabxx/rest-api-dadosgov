from fastapi import FastAPI
from app.core.database import Base, engine
from app.routers import beneficiario, instituicao, programa, pagamento

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(beneficiario.router)
app.include_router(instituicao.router)
app.include_router(programa.router)
app.include_router(pagamento.router)