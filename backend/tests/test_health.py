import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.core.config import settings


def test_app_initialization(client: TestClient):
    """Verifica se a aplicação FastAPI foi inicializada corretamente."""
    assert client.app is not None
    assert client.app.title == settings.PROJECT_NAME
    assert client.app.version == settings.VERSION


def test_health_check_root_endpoint(client: TestClient):
    """
    Testa a rota GET /health direta:
    - Código de status HTTP 200 (OK).
    - Estrutura completa do schema HealthCheckResponse.
    - Conteúdo correspondente às configurações do sistema.
    """
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert "status" in data
    assert "app_name" in data
    assert "version" in data
    assert "environment" in data

    assert data["status"] == "ok"
    assert data["app_name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT


def test_health_check_versioned_endpoint(client: TestClient):
    """Testa a disponibilidade do endpoint de integridade sob o prefixo versionado /api/v1/health."""
    response = client.get(f"{settings.API_V1_PREFIX}/health")
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["status"] == "ok"


def test_openapi_docs_availability(client: TestClient):
    """Verifica se a documentação OpenAPI/Swagger está acessível."""
    response = client.get("/docs")
    assert response.status_code == status.HTTP_200_OK

    openapi_json_response = client.get(f"{settings.API_V1_PREFIX}/openapi.json")
    assert openapi_json_response.status_code == status.HTTP_200_OK
    assert openapi_json_response.json()["info"]["title"] == settings.PROJECT_NAME
