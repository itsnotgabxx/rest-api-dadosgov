from typing import Type, Dict, Any, Optional
from sqlalchemy.orm import Query
from sqlalchemy import and_, or_

class FilterBuilder:
    """
    Constrói filtros dinâmicos para queries SQLAlchemy
    """
    
    def __init__(self, model_class: Type):
        self.model_class = model_class
        
    def apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """
        Aplica filtros dinâmicos na query
        """
        conditions = []
        
        for key, value in filters.items():
            if not value or value == '':  # Ignorar filtros vazios
                continue
                
            condition = self._build_condition(key, value)
            if condition is not None:
                conditions.append(condition)
        
        # Aplicar todas as condições com AND
        if conditions:
            query = query.filter(and_(*conditions))
            
        return query
    
    def _build_condition(self, key: str, value: Any):
        """Constrói uma condição individual"""
        
        # Busca geral (search em todos os campos de texto)
        if key == 'search':
            return self._build_search_condition(value)
        
        # Filtros com operadores
        if '_' in key:
            field_name, operator = key.rsplit('_', 1)
        else:
            field_name, operator = key, 'eq'
        
        # Verificar se o campo existe no modelo
        if not hasattr(self.model_class, field_name):
            return None
            
        column = getattr(self.model_class, field_name)
        
        # Aplicar operador
        if operator == 'eq':
            return column == value
        elif operator == 'like':
            return column.ilike(f'%{value}%')
        elif operator == 'gt':
            return column > value
        elif operator == 'gte':
            return column >= value
        elif operator == 'lt':
            return column < value
        elif operator == 'lte':
            return column <= value
            
        return column == value
    
    def _build_search_condition(self, search_term: str):
        """
        Busca geral em campos de texto do modelo
        """
        text_fields = []
        
        # Encontrar campos de texto/string no modelo
        for attr_name in dir(self.model_class):
            if not attr_name.startswith('_'):
                try:
                    attr = getattr(self.model_class, attr_name)
                    if hasattr(attr, 'type') and hasattr(attr.type, 'python_type'):
                        if attr.type.python_type == str:
                            text_fields.append(attr)
                except:
                    pass  # Ignorar erros
        
        # Criar condições OR para busca em todos os campos de texto
        if text_fields:
            conditions = [field.ilike(f'%{search_term}%') for field in text_fields]
            return or_(*conditions)
            
        return None