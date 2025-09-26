from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.services.user import create_user, authenticate_user, get_users, get_user_by_username, get_user_by_email
from app.core.deps import get_admin_user, get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"],
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Registra um novo usuário
    """
    # Verificar se username já existe
    if get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já está em uso"
        )
    
    # Verificar se email já existe
    if get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já está em uso"
        )
    
    # Criar usuário
    return create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login do usuário
    """
    user = authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Endpoint para compatibilidade com OAuth2PasswordRequestForm
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    """
    Retorna informações do usuário atual
    """
    return current_user

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user)
):
    """
    Lista todos os usuários (apenas admin)
    """
    users = get_users(db, skip=skip, limit=limit)
    return users