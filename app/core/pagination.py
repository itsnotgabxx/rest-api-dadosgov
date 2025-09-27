from typing import Type, Optional, Any
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc

def paginate_query(
    query: Query,
    page: int = 1,
    size: int = 10,
    sort_by: Optional[str] = None,
    sort_order: str = "asc",
    model_class: Optional[Type] = None
) -> dict:
    """
    Aplica paginação e ordenação em uma query
    """
    # Validações
    if page < 1:
        page = 1
    if size < 1 or size > 100:  # Limite máximo
        size = 10
    
    # Aplicar ordenação se especificada
    if sort_by and model_class:
        if hasattr(model_class, sort_by):
            column = getattr(model_class, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
    
    # Calcular offset
    offset = (page - 1) * size
    
    # Total de itens
    total = query.count()
    
    # Aplicar paginação
    items = query.offset(offset).limit(size).all()
    
    # Calcular metadados
    total_pages = (total + size - 1) // size  # Divisão com teto
    
    return {
        "items": items,
        "pagination": {
            "total": total,
            "page": page,
            "size": size,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }