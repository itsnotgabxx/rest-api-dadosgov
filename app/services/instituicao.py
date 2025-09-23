from sqlalchemy.orm import Session
from app.models.instituicao import Instituicao
from app.schemas.instituicao import InstituicaoCreate

def get_instituicao(db: Session, instituicao_id: int):
    return db.query(Instituicao).filter(Instituicao.id == instituicao_id).first()

def get_instituicoes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Instituicao).offset(skip).limit(limit).all()

def create_instituicao(db: Session, instituicao: InstituicaoCreate):
    db_instituicao = Instituicao(**instituicao.dict())
    db.add(db_instituicao)
    db.commit()
    db.refresh(db_instituicao)
    return db_instituicao