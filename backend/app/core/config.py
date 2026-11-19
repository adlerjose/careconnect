from functools import lru_cache
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações centrais da aplicação CareConnect.
    Carrega valores a partir de variáveis de ambiente ou arquivo .env local.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Identificação da API
    PROJECT_NAME: str = "CareConnect PI"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "Plataforma de acompanhamento pós-atendimento e triagem auxiliar via WhatsApp"
    API_V1_PREFIX: str = "/api/v1"

    # Ambiente de execução
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    BACKEND_CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Configurações reservadas para integrações futuras
    # Banco de Dados (PostgreSQL)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "careconnect_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changeme_in_production"

    # Provedor de IA (Google Gemini)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # Gateway de Mensagens (Evolution API)
    EVOLUTION_API_URL: str = ""
    EVOLUTION_API_KEY: str = ""
    EVOLUTION_WEBHOOK_SECRET: str = ""


@lru_cache
def get_settings() -> Settings:
    """Retorna uma instância singleton com as configurações validadas."""
    return Settings()


settings = get_settings()
