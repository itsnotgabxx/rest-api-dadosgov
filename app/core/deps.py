from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.services.user import get_user_by_username
from app.models.user import User

# Configurar o esquema de segurança Bearer
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Obtém o usuário atual a partir do token JWT
    """
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = get_user_by_username(db, username=token_data["username"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuário inativo"
        )
    
    return user

def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verifica se o usuário atual é admin
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Permissão de administrador necessária."
        )
    return current_user

def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Obtém usuário ativo (admin ou leitor)
    """
    return current_user