from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.programa import Programa, ProgramaCreate
from app.models.programa import Programa as ProgramaModel
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.core.pagination import paginate_query
from app.core.filters import FilterBuilder
from app.models.user import User

router = APIRouter(
    prefix="/programas",
    tags=["Programas"],
)

@router.get("/", response_model=Dict[str, Any])
def read_programas_enhanced(
    # Parâmetros de paginação
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query(None, description="Campo para ordenação: id, nome_chamada, programa_cnpq, grande_area"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Ordem: asc ou desc"),
    
    # Filtros dinâmicos
    search: Optional[str] = Query(None, description="Busca geral em todos os campos"),
    nome_chamada: Optional[str] = Query(None, description="Filtro por nome da chamada"),
    nome_chamada_like: Optional[str] = Query(None, description="Busca parcial no nome da chamada"),
    programa_cnpq: Optional[str] = Query(None, description="Filtro por programa CNPq"),
    programa_cnpq_like: Optional[str] = Query(None, description="Busca parcial no programa CNPq"),
    grande_area: Optional[str] = Query(None, description="Filtro por grande área"),
    area: Optional[str] = Query(None, description="Filtro por área"),
    subarea: Optional[str] = Query(None, description="Filtro por subárea"),
    
    # Dependências
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista programas com paginação, ordenação e filtros dinâmicos
    
    Exemplos:
    - /programas/?page=2&size=20
    - /programas/?search=produtividade
    - /programas/?grande_area=Ciências Exatas
    - /programas/?nome_chamada_like=bolsa&sort_by=nome_chamada
    """
    
    # Construir query base
    query = db.query(ProgramaModel)
    
    # Aplicar filtros
    filters = {
        'search': search,
        'nome_chamada': nome_chamada,
        'nome_chamada_like': nome_chamada_like,
        'programa_cnpq': programa_cnpq,
        'programa_cnpq_like': programa_cnpq_like,
        'grande_area': grande_area,
        'area': area,
        'subarea': subarea
    }
    
    # Remover filtros vazios
    filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    
    if filters:
        filter_builder = FilterBuilder(ProgramaModel)
        query = filter_builder.apply_filters(query, filters)
    
    # Aplicar paginação e ordenação
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=ProgramaModel
    )
    
    return {
        "data": result["items"],
        "pagination": result["pagination"],
        "filters_applied": filters
    }

@router.get("/areas", response_model=Dict[str, Any])
def get_areas_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas por áreas de conhecimento"""
    from sqlalchemy import func, distinct
    
    # Contar por grande área
    grande_areas = db.query(
        ProgramaModel.grande_area,
        func.count(ProgramaModel.id).label('total_programas')
    ).group_by(ProgramaModel.grande_area).all()
    
    # Contar áreas únicas
    total_areas = db.query(func.count(distinct(ProgramaModel.area))).scalar()
    total_subareas = db.query(func.count(distinct(ProgramaModel.subarea))).scalar()
    
    return {
        "total_programas": db.query(ProgramaModel).count(),
        "total_areas": total_areas,
        "total_subareas": total_subareas,
        "por_grande_area": [
            {"grande_area": area, "total_programas": total} 
            for area, total in grande_areas
        ]
    }

@router.get("/{programa_id}", response_model=Programa)
def read_programa_route(
    programa_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca programa por ID"""
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    return db_programa

@router.post("/", response_model=Programa)
def create_programa_route(
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria um novo programa (apenas admin)"""
    return create_programa(db=db, programa=programa)

@router.put("/{programa_id}", response_model=Programa)
def update_programa_route(
    programa_id: int,
    programa: ProgramaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza um programa (apenas admin)"""
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
    current_user: User = Depends(get_admin_user)
):
    """Deleta um programa (apenas admin)"""
    db_programa = get_programa(db, programa_id=programa_id)
    if db_programa is None:
        raise HTTPException(status_code=404, detail="Programa não encontrado")
    
    db.delete(db_programa)
    db.commit()
    return {"message": "Programa deletado com sucesso"}