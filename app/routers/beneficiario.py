from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.beneficiario import Beneficiario, BeneficiarioCreate
from app.services.beneficiario import get_beneficiario, create_beneficiario
from app.core.database import get_db

router = APIRouter()

@router.post("/beneficiarios/", response_model=Beneficiario)
def create_beneficiario_route(beneficiario: BeneficiarioCreate, db: Session = Depends(get_db)):
    return create_beneficiario(db=db, beneficiario=beneficiario)

@router.get("/beneficiarios/{beneficiario_id}", response_model=Beneficiario)
def read_beneficiario_route(beneficiario_id: int, db: Session = Depends(get_db)):
    db_beneficiario = get_beneficiario(db, beneficiario_id=beneficiario_id)
    if db_beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    return db_beneficiario