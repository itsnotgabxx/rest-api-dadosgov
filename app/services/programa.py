from sqlalchemy.orm import Session
from app.models.programa import Programa
from app.schemas.programa import ProgramaCreate

def get_programa(db: Session, programa_id: int):
    return db.query(Programa).filter(Programa.id == programa_id).first()

def get_programas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Programa).offset(skip).limit(limit).all()

def create_programa(db: Session, programa: ProgramaCreate):
    db_programa = Programa(**programa.dict())
    db.add(db_programa)
    db.commit()
    db.refresh(db_programa)
    return db_programa