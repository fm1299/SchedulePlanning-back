
'''
En Pydantic v2 esa clase interna Config (comentada actualmente) ya no tiene efecto; 
la configuración debe ir en model_config. Cambiar el archivo a pydantic
'''




from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List



class Settings(BaseSettings):
    PROJECT_NAME: str = "Sistema Asignación Aulas UNSA"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Redis (optional for caching)
    REDIS_URL: str = "redis://localhost:6379"
    
    #class Config:
    #    env_file = ".env"
    #    case_sensitive = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )




settings = Settings()
