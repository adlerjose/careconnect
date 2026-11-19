from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    """Schema de resposta do endpoint de verificação de integridade."""
    status: str = Field(..., examples=["ok"], description="Status da aplicação")
    app_name: str = Field(..., examples=["CareConnect PI"], description="Nome da aplicação")
    version: str = Field(..., examples=["0.1.0"], description="Versão atual da API")
    environment: str = Field(..., examples=["development"], description="Ambiente de execução")


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificação de integridade da API",
    description="Retorna o status operacional da aplicação e metadados básicos.",
    tags=["Health"],
)
async def health_check() -> HealthCheckResponse:
    return HealthCheckResponse(
        status="ok",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
