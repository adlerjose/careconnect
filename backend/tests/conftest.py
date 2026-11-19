import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Garante que o diretório 'backend' esteja no sys.path durante a execução dos testes
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Fixture que fornece um cliente de testes HTTP para a aplicação FastAPI."""
    with TestClient(app) as test_client:
        yield test_client
