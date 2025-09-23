from sqlalchemy.orm import Session
from app.models.beneficiario import Beneficiario
from app.schemas.beneficiario import BeneficiarioCreate

def get_beneficiario(db: Session, beneficiario_id: int):
    return db.query(Beneficiario).filter(Beneficiario.id == beneficiario_id).first()

def create_beneficiario(db: Session, beneficiario: BeneficiarioCreate):
    db_beneficiario = Beneficiario(**beneficiario.dict())
    db.add(db_beneficiario)
    db.commit()
    db.refresh(db_beneficiario)
    return db_beneficiario