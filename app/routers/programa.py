from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.programa import Programa, ProgramaCreate
from app.services.programa import get_programa, get_programas, create_programa
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/programas",
    tags=["Programas"],
)

@router.post("/", response_model=Programa)
def create_programa_route(
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode criar
):
    """
    Cria um novo programa (apenas admin)
    """
    return create_programa(db=db, programa=programa)

@router.get("/{programa_id}", response_model=Programa)
def read_programa_route(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Busca programa por ID (usuários autenticados)
    """
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return db_programa

@router.get("/", response_model=List[Programa])
def read_programas_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista programas (usuários autenticados)
    """
    programas = get_programas(db, skip=skip, limit=limit)
    return programas

@router.put("/{programa_id}", response_model=Programa)
def update_programa_route(
    programa_id: int,
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode atualizar
):
    """
    Atualiza um programa (apenas admin)
    """
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    for key, value in programa.dict(exclude_unset=True).items():
        setattr(db_programa, key, value)
    
    db.commit()
    db.refresh(db_programa)
    return db_programa

@router.delete("/{programa_id}")
def delete_programa_route(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode deletar
):
    """
    Deleta um programa (apenas admin)
    """
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    db.delete(db_programa)
    db.commit()
    return {"message": "Programa deletado com sucesso"}