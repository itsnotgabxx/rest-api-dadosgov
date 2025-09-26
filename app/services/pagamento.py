from sqlalchemy.orm import Session
from app.models.pagamento import Pagamento
from app.schemas.pagamento import PagamentoCreate

def get_pagamento(db: Session, pagamento_id: int):
    return db.query(Pagamento).filter(Pagamento.id == pagamento_id).first()

def get_pagamentos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Pagamento).offset(skip).limit(limit).all()

def create_pagamento(db: Session, pagamento: PagamentoCreate):
    db_pagamento = Pagamento(**pagamento.dict())
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento