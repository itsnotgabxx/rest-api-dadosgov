from sqlalchemy.orm import Session
from app.models.beneficiario import Beneficiario
from app.schemas.beneficiario import BeneficiarioCreate

def get_beneficiario(db: Session, beneficiario_id: int):
    return db.query(Beneficiario).filter(Beneficiario.id == beneficiario_id).first()

def get_beneficiarios(db: Session, skip: int = 0, limit: int = 100):  # ← Adicionar esta função
    return db.query(Beneficiario).offset(skip).limit(limit).all()

def create_beneficiario(db: Session, beneficiario: BeneficiarioCreate):
    db_beneficiario = Beneficiario(**beneficiario.dict())
    db.add(db_beneficiario)
    db.commit()
    db.refresh(db_beneficiario)
    return db_beneficiario