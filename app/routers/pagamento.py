from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date
from app.schemas.pagamento import Pagamento, PagamentoCreate
from app.models.pagamento import Pagamento as PagamentoModel
from app.services.pagamento import get_pagamento, create_pagamento
from app.core.database import get_db
from app.core.deps import get_current_active_user, get_admin_user
from app.core.pagination import paginate_query
from app.core.filters import FilterBuilder
from app.models.user import User

router = APIRouter(
    prefix="/pagamentos",
    tags=["Pagamentos"],
)

@router.get("/", response_model=Dict[str, Any])
def read_pagamentos_enhanced(
    # Parâmetros de paginação
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(10, ge=1, le=100, description="Itens por página"),
    sort_by: Optional[str] = Query(None, description="Campo para ordenação: id, ano_referencia, valor_pago, data_inicio"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Ordem: asc ou desc"),
    
    # Filtros básicos
    search: Optional[str] = Query(None, description="Busca geral em todos os campos"),
    ano_referencia: Optional[int] = Query(None, description="Filtro por ano"),
    modalidade: Optional[str] = Query(None, description="Filtro por modalidade"),
    linha_fomento: Optional[str] = Query(None, description="Filtro por linha de fomento"),
    
    # Filtros de valor
    valor_min: Optional[float] = Query(None, description="Valor mínimo"),
    valor_max: Optional[float] = Query(None, description="Valor máximo"),
    
    # Filtros de data
    data_inicio_desde: Optional[date] = Query(None, description="Data início desde (YYYY-MM-DD)"),
    data_inicio_ate: Optional[date] = Query(None, description="Data início até (YYYY-MM-DD)"),
    
    # Filtros por relacionamento
    beneficiario_id: Optional[int] = Query(None, description="ID do beneficiário"),
    instituicao_id: Optional[int] = Query(None, description="ID da instituição"),
    programa_id: Optional[int] = Query(None, description="ID do programa"),
    
    # Filtros avançados de texto
    titulo_projeto_like: Optional[str] = Query(None, description="Busca no título do projeto"),
    processo: Optional[str] = Query(None, description="Número do processo"),
    
    # Dependências
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista pagamentos com paginação, ordenação e filtros avançados"""
    
    # Construir query base
    query = db.query(PagamentoModel)
    
    # Aplicar filtros simples
    filters = {}
    
    # Filtros básicos
    if search:
        filters['search'] = search
    if ano_referencia:
        filters['ano_referencia'] = ano_referencia
    if modalidade:
        filters['modalidade'] = modalidade
    if linha_fomento:
        filters['linha_fomento'] = linha_fomento
    if processo:
        filters['processo'] = processo
    if titulo_projeto_like:
        filters['titulo_projeto_like'] = titulo_projeto_like
        
    # Filtros de relacionamento
    if beneficiario_id:
        filters['fk_beneficiario'] = beneficiario_id
    if instituicao_id:
        filters['fk_instituicao'] = instituicao_id
    if programa_id:
        filters['fk_programa'] = programa_id
    
    # Aplicar filtros básicos
    if filters:
        filter_builder = FilterBuilder(PagamentoModel)
        query = filter_builder.apply_filters(query, filters)
    
    # Aplicar filtros de valor manualmente
    if valor_min is not None:
        query = query.filter(PagamentoModel.valor_pago >= valor_min)
    if valor_max is not None:
        query = query.filter(PagamentoModel.valor_pago <= valor_max)
        
    # Aplicar filtros de data manualmente
    if data_inicio_desde:
        query = query.filter(PagamentoModel.data_inicio >= data_inicio_desde)
    if data_inicio_ate:
        query = query.filter(PagamentoModel.data_inicio <= data_inicio_ate)
    
    # Aplicar paginação e ordenação
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=PagamentoModel
    )
    
    # Converter objetos SQLAlchemy para dicionários
    pagamentos_data = [
        {
            "id": item.id,
            "ano_referencia": item.ano_referencia,
            "processo": item.processo,
            "modalidade": item.modalidade,
            "linha_fomento": item.linha_fomento,
            "valor_pago": item.valor_pago,
            "data_inicio": item.data_inicio.isoformat() if item.data_inicio else None,
            "data_fim": item.data_fim.isoformat() if item.data_fim else None,
            "titulo_projeto": item.titulo_projeto,
            "fk_beneficiario": item.fk_beneficiario,
            "fk_instituicao": item.fk_instituicao,
            "fk_programa": item.fk_programa
        }
        for item in result["items"]
    ]
    
    return {
        "data": pagamentos_data,
        "pagination": result["pagination"],
        "filters_applied": {
            **filters,
            "valor_min": valor_min,
            "valor_max": valor_max,
            "data_inicio_desde": data_inicio_desde,
            "data_inicio_ate": data_inicio_ate
        }
    }

@router.get("/stats", response_model=Dict[str, Any])
def get_pagamentos_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Estatísticas dos pagamentos"""
    from sqlalchemy import func
    
    # Estatísticas básicas
    total_pagamentos = db.query(PagamentoModel).count()
    valor_total = db.query(func.sum(PagamentoModel.valor_pago)).scalar() or 0
    valor_medio = db.query(func.avg(PagamentoModel.valor_pago)).scalar() or 0
    
    # Por modalidade
    por_modalidade = db.query(
        PagamentoModel.modalidade,
        func.count(PagamentoModel.id).label('total'),
        func.sum(PagamentoModel.valor_pago).label('valor_total')
    ).group_by(PagamentoModel.modalidade).all()
    
    # Por ano
    por_ano = db.query(
        PagamentoModel.ano_referencia,
        func.count(PagamentoModel.id).label('total'),
        func.sum(PagamentoModel.valor_pago).label('valor_total')
    ).group_by(PagamentoModel.ano_referencia).all()
    
    return {
        "resumo": {
            "total_pagamentos": total_pagamentos,
            "valor_total": float(valor_total),
            "valor_medio": float(valor_medio)
        },
        "por_modalidade": [
            {
                "modalidade": modalidade or "Não informado",
                "total_pagamentos": total,
                "valor_total": float(valor or 0)
            }
            for modalidade, total, valor in por_modalidade
        ],
        "por_ano": [
            {
                "ano": ano,
                "total_pagamentos": total,
                "valor_total": float(valor or 0)
            }
            for ano, total, valor in por_ano
        ]
    }

@router.get("/beneficiario/{beneficiario_id}", response_model=Dict[str, Any])
def read_pagamentos_by_beneficiario(
    beneficiario_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query("data_inicio", description="Campo para ordenação"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista pagamentos de um beneficiário específico com paginação"""
    
    query = db.query(PagamentoModel).filter(PagamentoModel.fk_beneficiario == beneficiario_id)
    
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=PagamentoModel
    )
    
    # Converter objetos SQLAlchemy para dicionários
    pagamentos_data = [
        {
            "id": item.id,
            "ano_referencia": item.ano_referencia,
            "processo": item.processo,
            "modalidade": item.modalidade,
            "linha_fomento": item.linha_fomento,
            "valor_pago": item.valor_pago,
            "data_inicio": item.data_inicio.isoformat() if item.data_inicio else None,
            "data_fim": item.data_fim.isoformat() if item.data_fim else None,
            "titulo_projeto": item.titulo_projeto,
            "fk_beneficiario": item.fk_beneficiario,
            "fk_instituicao": item.fk_instituicao,
            "fk_programa": item.fk_programa
        }
        for item in result["items"]
    ]
    
    return {
        "beneficiario_id": beneficiario_id,
        "data": pagamentos_data,
        "pagination": result["pagination"]
    }

@router.get("/instituicao/{instituicao_id}", response_model=Dict[str, Any])
def read_pagamentos_by_instituicao(
    instituicao_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query("data_inicio", description="Campo para ordenação"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista pagamentos de uma instituição específica com paginação"""
    
    query = db.query(PagamentoModel).filter(PagamentoModel.fk_instituicao == instituicao_id)
    
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=PagamentoModel
    )
    
    # Converter para dicionários
    pagamentos_data = [
        {
            "id": item.id,
            "ano_referencia": item.ano_referencia,
            "processo": item.processo,
            "modalidade": item.modalidade,
            "linha_fomento": item.linha_fomento,
            "valor_pago": item.valor_pago,
            "data_inicio": item.data_inicio.isoformat() if item.data_inicio else None,
            "data_fim": item.data_fim.isoformat() if item.data_fim else None,
            "titulo_projeto": item.titulo_projeto,
            "fk_beneficiario": item.fk_beneficiario,
            "fk_instituicao": item.fk_instituicao,
            "fk_programa": item.fk_programa
        }
        for item in result["items"]
    ]
    
    return {
        "instituicao_id": instituicao_id,
        "data": pagamentos_data,
        "pagination": result["pagination"]
    }

@router.get("/programa/{programa_id}", response_model=Dict[str, Any])
def read_pagamentos_by_programa(
    programa_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    sort_by: Optional[str] = Query("data_inicio", description="Campo para ordenação"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Lista pagamentos de um programa específico com paginação"""
    
    query = db.query(PagamentoModel).filter(PagamentoModel.fk_programa == programa_id)
    
    result = paginate_query(
        query=query,
        page=page,
        size=size,
        sort_by=sort_by,
        sort_order=sort_order,
        model_class=PagamentoModel
    )
    
    # Converter para dicionários
    pagamentos_data = [
        {
            "id": item.id,
            "ano_referencia": item.ano_referencia,
            "processo": item.processo,
            "modalidade": item.modalidade,
            "linha_fomento": item.linha_fomento,
            "valor_pago": item.valor_pago,
            "data_inicio": item.data_inicio.isoformat() if item.data_inicio else None,
            "data_fim": item.data_fim.isoformat() if item.data_fim else None,
            "titulo_projeto": item.titulo_projeto,
            "fk_beneficiario": item.fk_beneficiario,
            "fk_instituicao": item.fk_instituicao,
            "fk_programa": item.fk_programa
        }
        for item in result["items"]
    ]
    
    return {
        "programa_id": programa_id,
        "data": pagamentos_data,
        "pagination": result["pagination"]
    }

@router.get("/{pagamento_id}", response_model=Pagamento)
def read_pagamento_route(
    pagamento_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Busca pagamento por ID"""
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return db_pagamento

@router.post("/", response_model=Pagamento)
def create_pagamento_route(
    pagamento: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Cria um novo pagamento (apenas admin)"""
    return create_pagamento(db=db, pagamento=pagamento)

@router.put("/{pagamento_id}", response_model=Pagamento)
def update_pagamento_route(
    pagamento_id: int,
    pagamento: PagamentoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user)
):
    """Atualiza um pagamento (apenas admin)"""
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
    current_user: User = Depends(get_admin_user)
):
    """Deleta um pagamento (apenas admin)"""
    db_pagamento = get_pagamento(db, pagamento_id=pagamento_id)
    if db_pagamento is None:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    
    db.delete(db_pagamento)
    db.commit()
    return {"message": "Pagamento deletado com sucesso"}