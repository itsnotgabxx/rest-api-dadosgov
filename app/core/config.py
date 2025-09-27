import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Configurações da aplicação
    """
    # Aplicação
    app_name: str = "API CNPq - Dados Abertos"
    app_version: str = "1.0.0"
    app_env: str = "development"
    debug: bool = False
    
    # Servidor
    host: str = "127.0.0.1"
    port: int = 8000
    
    # JWT
    secret_key: str = "cnpq-api-dev-key-2024-rest-api-dadosgov-projeto-academico-seguro"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # Banco de dados
    database_url: str = "sqlite:///./sql_app.db"
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Logs
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()