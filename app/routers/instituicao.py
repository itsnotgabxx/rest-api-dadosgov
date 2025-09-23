from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.instituicao import Instituicao, InstituicaoCreate
from app.services.instituicao import get_instituicao, get_instituicoes, create_instituicao
from app.core.database import get_db

router = APIRouter(
    prefix="/instituicoes",
    tags=["Instituições"],
)

@router.post("/", response_model=Instituicao)
def create_instituicao_route(instituicao: InstituicaoCreate, db: Session = Depends(get_db)):
    return create_instituicao(db=db, instituicao=instituicao)

@router.get("/{instituicao_id}", response_model=Instituicao)
def read_instituicao_route(instituicao_id: int, db: Session = Depends(get_db)):
    db_instituicao = get_instituicao(db, instituicao_id=instituicao_id)
    if db_instituicao is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return db_instituicao

@router.get("/", response_model=List[Instituicao])
def read_instituicoes_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    instituicoes = get_instituicoes(db, skip=skip, limit=limit)
    return instituicoes