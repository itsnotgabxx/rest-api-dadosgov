from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.pagamento import Pagamento, PagamentoCreate
from app.services.pagamento import get_pagamento, get_pagamentos, create_pagamento
from app.core.database import get_db

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)

@router.post("/", response_model=Pagamento)
def create_pagamento_route(pagamento: PagamentoCreate, db: Session = Depends(get_db)):
    return create_pagamento(db=db, pagamento=pagamento)

@router.get("/{pagamento_id}", response_model=Pagamento)
def read_pagamento_route(pagamento_id: int, db: Session = Depends(get_db)):
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return db_pagamento

@router.get("/", response_model=List[Pagamento])
def read_pagamentos_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    pagamentos = get_pagamentos(db, skip=skip, limit=limit)
    return pagamentos