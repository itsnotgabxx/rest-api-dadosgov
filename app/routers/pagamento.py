from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.pagamento import Pagamento, PagamentoCreate
from app.services.pagamento import get_pagamento, get_pagamentos, create_pagamento
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)

@router.post("/", response_model=Pagamento)
def create_pagamento_route(
    pagamento: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode criar
):
    """
    Cria um novo pagamento (apenas admin)
    """
    return create_pagamento(db=db, pagamento=pagamento)

@router.get("/{pagamento_id}", response_model=Pagamento)
def read_pagamento_route(
    pagamento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Busca pagamento por ID (usuários autenticados)
    """
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return db_pagamento

@router.get("/", response_model=List[Pagamento])
def read_pagamentos_route(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista pagamentos (usuários autenticados)
    """
    pagamentos = get_pagamentos(db, skip=skip, limit=limit)
    return pagamentos

@router.get("/beneficiario/{beneficiario_id}", response_model=List[Pagamento])
def read_pagamentos_by_beneficiario(
    beneficiario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista pagamentos por beneficiário (usuários autenticados)
    """
    pagamentos = db.query(Pagamento).filter(Pagamento.fk_beneficiario == beneficiario_id).all()
    return pagamentos

@router.get("/instituicao/{instituicao_id}", response_model=List[Pagamento])
def read_pagamentos_by_instituicao(
    instituicao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista pagamentos por instituição (usuários autenticados)
    """
    pagamentos = db.query(Pagamento).filter(Pagamento.fk_instituicao == instituicao_id).all()
    return pagamentos

@router.get("/programa/{programa_id}", response_model=List[Pagamento])
def read_pagamentos_by_programa(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)  # Qualquer usuário autenticado
):
    """
    Lista pagamentos por programa (usuários autenticados)
    """
    pagamentos = db.query(Pagamento).filter(Pagamento.fk_programa == programa_id).all()
    return pagamentos

@router.put("/{pagamento_id}", response_model=Pagamento)
def update_pagamento_route(
    pagamento_id: int,
    pagamento: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode atualizar
):
    """
    Atualiza um pagamento (apenas admin)
    """
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    for key, value in pagamento.dict(exclude_unset=True).items():
        setattr(db_pagamento, key, value)
    
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento

@router.delete("/{pagamento_id}")
def delete_pagamento_route(
    pagamento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)  # Apenas admin pode deletar
):
    """
    Deleta um pagamento (apenas admin)
    """
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    db.delete(db_pagamento)
    db.commit()
    return {"message": "Pagamento deletado com sucesso"}