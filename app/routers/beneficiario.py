from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.beneficiario import Beneficiario, BeneficiarioCreate
from app.services.beneficiario import get_beneficiario, create_beneficiario, get_beneficiarios
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/beneficiarios",
    tags=["Beneficiários"],
)

@router.post("/", response_model=Beneficiario)
def create_beneficiario_route(
    beneficiario: BeneficiarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode criar
):
    """
    Cria um novo beneficiário (apenas admin)
    """
    return create_beneficiario(db=db, beneficiario=beneficiario)

@router.get("/{beneficiario_id}", response_model=Beneficiario)
def read_beneficiario_route(
    beneficiario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Busca beneficiário por ID (usuários autenticados)
    """
    db_beneficiario = get_beneficiario(db, beneficiario_id=beneficiario_id)
    if db_beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    return db_beneficiario

@router.get("/", response_model=List[Beneficiario])
def read_beneficiarios_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista beneficiários (usuários autenticados)
    """
    beneficiarios = get_beneficiarios(db, skip=skip, limit=limit)
    return beneficiarios