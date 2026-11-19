import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Assegura que o diretório 'backend' esteja no sys.path para imports absolutos
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import api_router
from app.api.routes.health import router as health_router
from app.core.config import settings
from app.core.logging import get_logger, setup_logging

logger = get_logger("careconnect.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida da aplicação FastAPI: inicialização e finalização."""
    setup_logging()
    logger.info(
        f"Iniciando {settings.PROJECT_NAME} v{settings.VERSION} [{settings.ENVIRONMENT}]"
    )
    yield
    logger.info(f"Encerrando {settings.PROJECT_NAME}")


def create_application() -> FastAPI:
    """Fábrica de criação da aplicação FastAPI com configurações centrais."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    # Configuração de CORS para comunicação com frontend React
    if settings.BACKEND_CORS_ORIGINS:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Rota raiz de integridade (GET /health) para monitoramento direto
    application.include_router(health_router, tags=["Health"])

    # Rotas versionadas sob o prefixo da API (/api/v1/...)
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
