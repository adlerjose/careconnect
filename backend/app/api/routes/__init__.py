from fastapi import APIRouter
from app.api.routes import health

api_router = APIRouter()

# Rota de health check sob o prefixo da API versionada (/api/v1/health)
api_router.include_router(health.router)

# Ponto de extensão para novos módulos (desenvolvidos nas próximas tarefas):
# from app.modules.patients.routes import router as patients_router
# from app.modules.messages.routes import router as messages_router
# from app.modules.triage.routes import router as triage_router
# from app.modules.ai.routes import router as ai_router
#
# api_router.include_router(patients_router, prefix="/patients", tags=["Patients"])
# api_router.include_router(messages_router, prefix="/messages", tags=["Messages"])
# api_router.include_router(triage_router, prefix="/triage", tags=["Triage"])
# api_router.include_router(ai_router, prefix="/ai", tags=["AI"])
