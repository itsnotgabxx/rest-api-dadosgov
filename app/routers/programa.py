from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.programa import Programa, ProgramaCreate
from app.services.programa import get_programa, get_programas, create_programa
from app.core.database import get_db

router = APIRouter(
    prefix="/programas",
    tags=["Programas"],
)

@router.post("/", response_model=Programa)
def create_programa_route(programa: ProgramaCreate, db: Session = Depends(get_db)):
    return create_programa(db=db, programa=programa)

@router.get("/{programa_id}", response_model=Programa)
def read_programa_route(programa_id: int, db: Session = Depends(get_db)):
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return db_programa

@router.get("/", response_model=List[Programa])
def read_programas_route(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    programas = get_programas(db, skip=skip, limit=limit)
    return programas