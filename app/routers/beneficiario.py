from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.schemas.beneficiario import Beneficiario, BeneficiarioCreate
from app.services.beneficiario import get_beneficiario, create_beneficiario
from app.models.beneficiario import Beneficiario as BeneficiarioModel
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.core.pagination import paginate_query
from app.core.filters import FilterBuilder
from app.models.user import User

router = APIRouter(
    prefix="/beneficiarios",
    tags=["Beneficiários"],
)

@router.get("/", response_model=Dict[str, Any])
def read_beneficiarios_enhanced(
    # Parâmetros de paginação
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query(None, description="Campo para ordenação: id, nome, categoria_nivel"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Ordem: asc ou desc"),
    
    # Filtros dinâmicos
    search: Optional[str] = Query(None, description="Busca geral em todos os campos"),
    nome: Optional[str] = Query(None, description="Filtro exato por nome"),
    nome_like: Optional[str] = Query(None, description="Busca parcial no nome"),
    categoria_nivel: Optional[str] = Query(None, description="Filtro por categoria/nível"),
    cpf_anonimizado: Optional[str] = Query(None, description="Filtro por CPF anonimizado"),
    
    # Dependências
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Lista beneficiários com paginação, ordenação e filtros
    
    Exemplos:
    - /beneficiarios/?page=2&size=20
    - /beneficiarios/?search=silva
    - /beneficiarios/?categoria_nivel=Doutor
    - /beneficiarios/?nome_like=maria&sort_by=nome&sort_order=desc
    """
    
    # Construir query base
    query = db.query(BeneficiarioModel)
    
    # Aplicar filtros
    filters = {
        'search': search,
        'nome': nome,
        'nome_like': nome_like,
        'categoria_nivel': categoria_nivel,
        'cpf_anonimizado': cpf_anonimizado
    }
    
    # Remover filtros vazios
    filters = {k: v for k, v in filters.items() if v is not None and v != ''}
    
    if filters:
        filter_builder = FilterBuilder(BeneficiarioModel)
        query = filter_builder.apply_filters(query, filters)
    
    # Aplicar paginação e ordenação
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=BeneficiarioModel
    )
    
    # CORREÇÃO: Converter objetos SQLAlchemy para dicionários serializáveis
    beneficiarios_data = [
        {
            "id": item.id,
            "nome": item.nome,
            "cpf_anonimizado": item.cpf_anonimizado,
            "categoria_nivel": item.categoria_nivel
        }
        for item in result["items"]
    ]
    
    return {
        "data": beneficiarios_data,
        "pagination": result["pagination"],
        "filters_applied": filters
    }

@router.get("/stats", response_model=Dict[str, Any])
def get_beneficiarios_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas dos beneficiários"""
    from sqlalchemy import func
    
    total_beneficiarios = db.query(BeneficiarioModel).count()
    por_categoria = db.query(
        BeneficiarioModel.categoria_nivel, 
        func.count(BeneficiarioModel.id).label('total')
    ).group_by(BeneficiarioModel.categoria_nivel).all()
    
    return {
        "total_beneficiarios": total_beneficiarios,
        "por_categoria": [
            {"categoria_nivel": categoria or "Não informado", "total": total} 
            for categoria, total in por_categoria
        ]
    }

@router.get("/{beneficiario_id}", response_model=Beneficiario)
def read_beneficiario_route(
    beneficiario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca beneficiário por ID"""
    db_beneficiario = get_beneficiario(db, beneficiario_id=beneficiario_id)
    if db_beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    return db_beneficiario

@router.post("/", response_model=Beneficiario)
def create_beneficiario_route(
    beneficiario: BeneficiarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria um novo beneficiário (apenas admin)"""
    return create_beneficiario(db=db, beneficiario=beneficiario)

@router.put("/{beneficiario_id}", response_model=Beneficiario)
def update_beneficiario_route(
    beneficiario_id: int,
    beneficiario: BeneficiarioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza um beneficiário (apenas admin)"""
    db_beneficiario = get_beneficiario(db, beneficiario_id=beneficiario_id)
    if db_beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    
    for key, value in beneficiario.dict(exclude_unset=True).items():
        setattr(db_beneficiario, key, value)
    
    db.commit()
    db.refresh(db_beneficiario)
    return db_beneficiario

@router.delete("/{beneficiario_id}")
def delete_beneficiario_route(
    beneficiario_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Deleta um beneficiário (apenas admin)"""
    db_beneficiario = get_beneficiario(db, beneficiario_id=beneficiario_id)
    if db_beneficiario is None:
        raise HTTPException(status_code=404, detail="Beneficiário não encontrado")
    
    db.delete(db_beneficiario)
    db.commit()
    return {"message": "Beneficiário deletado com sucesso"}