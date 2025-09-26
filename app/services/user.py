from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash, verify_password

def get_user_by_username(db: Session, username: str):
    """
    Busca usuário por username
    """
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    """
    Busca usuário por email
    """
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """
    Cria um novo usuário
    """
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    """
    Autentica usuário
    """
    user = get_user_by_username(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista usuários (apenas admin)
    """
    return db.query(User).offset(skip).limit(limit).all()