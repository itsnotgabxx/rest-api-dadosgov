from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.instituicao import Instituicao, InstituicaoCreate
from app.models.instituicao import Instituicao as InstituicaoModel
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.core.pagination import paginate_query
from app.core.filters import FilterBuilder
from app.models.user import User

router = APIRouter(
    prefix="/instituicoes",
    tags=["Instituições"],
)

@router.get("/", response_model=Dict[str, Any])
def read_instituicoes_enhanced(
    # Parâmetros de paginação
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query(None, description="Campo para ordenação: id, nome, sigla, cidade, uf"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Ordem: asc ou desc"),
    
    # Filtros dinâmicos
    search: Optional[str] = Query(None, description="Busca geral em todos os campos"),
    nome: Optional[str] = Query(None, description="Filtro exato por nome"),
    nome_like: Optional[str] = Query(None, description="Busca parcial no nome"),
    sigla: Optional[str] = Query(None, description="Filtro por sigla"),
    cidade: Optional[str] = Query(None, description="Filtro por cidade"),
    cidade_like: Optional[str] = Query(None, description="Busca parcial na cidade"),
    uf: Optional[str] = Query(None, description="Filtro por UF"),
    pais: Optional[str] = Query(None, description="Filtro por país"),
    
    # Dependências
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista instituições com paginação, ordenação e filtros dinâmicos
    
    Exemplos:
    - /instituicoes/?page=2&size=20
    - /instituicoes/?search=universidade
    - /instituicoes/?nome_like=federal&uf=SP
    - /instituicoes/?sort_by=nome&sort_order=desc
    - /instituicoes/?cidade=São Paulo&pais=Brasil
    """
    
    # Construir query base
    query = db.query(InstituicaoModel)
    
    # Aplicar filtros
    filters = {
        'search': search,
        'nome': nome,
        'nome_like': nome_like,
        'sigla': sigla,
        'cidade': cidade,
        'cidade_like': cidade_like,
        'uf': uf,
        'pais': pais
    }
    
    # Remover filtros vazios
    filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    
    if filters:
        filter_builder = FilterBuilder(InstituicaoModel)
        query = filter_builder.apply_filters(query, filters)
    
    # Aplicar paginação e ordenação
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=InstituicaoModel
    )
    
    return {
        "data": result["items"],
        "pagination": result["pagination"],
        "filters_applied": filters
    }

@router.get("/stats", response_model=Dict[str, Any])
def get_instituicoes_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas das instituições"""
    from sqlalchemy import func
    
    total_instituicoes = db.query(InstituicaoModel).count()
    por_uf = db.query(
        InstituicaoModel.uf, 
        func.count(InstituicaoModel.id).label('total')
    ).group_by(InstituicaoModel.uf).all()
    
    por_pais = db.query(
        InstituicaoModel.pais,
        func.count(InstituicaoModel.id).label('total')
    ).group_by(InstituicaoModel.pais).all()
    
    return {
        "total_instituicoes": total_instituicoes,
        "por_uf": [{"uf": uf, "total": total} for uf, total in por_uf],
        "por_pais": [{"pais": pais, "total": total} for pais, total in por_pais]
    }

@router.get("/{instituicao_id}", response_model=Instituicao)
def read_instituicao_route(
    instituicao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca instituição por ID"""
    db_instituicao = get_instituicao(db, instituicao_id=instituicao_id)
    if db_instituicao is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    return db_instituicao

@router.post("/", response_model=Instituicao)
def create_instituicao_route(
    instituicao: InstituicaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria uma nova instituição (apenas admin)"""
    return create_instituicao(db=db, instituicao=instituicao)

@router.put("/{instituicao_id}", response_model=Instituicao)
def update_instituicao_route(
    instituicao_id: int,
    instituicao: InstituicaoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza uma instituição (apenas admin)"""
    db_instituicao = get_instituicao(db, instituicao_id=instituicao_id)
    if db_instituicao is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    
    for key, value in instituicao.dict(exclude_unset=True).items():
        setattr(db_instituicao, key, value)
    
    db.commit()
    db.refresh(db_instituicao)
    return db_instituicao

@router.delete("/{instituicao_id}")
def delete_instituicao_route(
    instituicao_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deleta uma instituição (apenas admin)"""
    db_instituicao = get_instituicao(db, instituicao_id=instituicao_id)
    if db_instituicao is None:
        raise HTTPException(status_code=404, detail="Instituição não encontrada")
    
    db.delete(db_instituicao)
    db.commit()
    return {"message": "Instituição deletada com sucesso"}