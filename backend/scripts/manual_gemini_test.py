"""
Script para execução de teste manual de integração real com o Google Gemini.

Requisitos:
- Definir a chave no arquivo .env (GEMINI_API_KEY="...") ou via terminal:
    export GEMINI_API_KEY="sua_chave"
    python scripts/manual_gemini_test.py
"""

import asyncio
import os
import sys
from pathlib import Path

# Assegura que o diretório 'backend' esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Carrega variáveis de ambiente tanto do backend quanto da raiz
from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

from app.core.config import settings
from app.modules.ai.pipelines.extraction_pipeline import ClinicalExtractionPipeline
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.gemini_provider import GeminiProvider


async def main():
    api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    if not api_key or not api_key.strip():
        print("\n[ERRO] Variável GEMINI_API_KEY não foi encontrada.")
        print("Preencha a variável GEMINI_API_KEY no arquivo .env ou exporte-a via:")
        print("  export GEMINI_API_KEY='sua_chave'\n")
        sys.exit(1)

    print("==================================================================")
    print("CareConnect PI - Teste Manual de Integração Real com Google Gemini")
    print("==================================================================")

    provider = GeminiProvider(api_key=api_key)
    print(f"Provedor: {provider.provider_name}")
    print(f"Modelo configurado: {provider.model_name}")
    print(f"Timeout configurado: {provider.timeout}s")
    print(f"Configurado: {provider.is_configured()}\n")

    pipeline = ClinicalExtractionPipeline(provider=provider)

    # Exemplo sintético de mensagem de paciente pós-atendimento
    sample_message = AIMessageInput(
        message_id="manual-test-msg-001",
        patient_id="synthetic-patient-1234",
        message_type=MessageType.TEXT,
        content=(
            "Olá doutor, fiz a cirurgia de apendicite há 3 dias. Hoje comecei a sentir "
            "uma dor moderada perto dos pontos e um pouco de febre (37.8C). "
            "Tomei um comprimido de dipirona 500mg faz 1 hora mas a febre continua."
        ),
    )

    print("Enviando relato sintético ao Gemini:")
    print(f"Relato: '{sample_message.content}'\n")

    try:
        result = await pipeline.run(sample_message)
        print("------------------------------------------------------------------")
        print("Resultado Estruturado Recebido (ClinicalExtractionResult):")
        print("------------------------------------------------------------------")
        print(f"Sintomas extraídos:       {result.symptoms}")
        print(f"Duração relatada:         {result.duration}")
        print(f"Medicamentos mencionados: {result.medications}")
        print(f"Resumo clínico:           {result.clinical_summary}")
        print(f"Confiança estimada (0-1): {result.confidence}")
        print(f"Revisão humana requerida: {result.requires_human_review}")
        print("------------------------------------------------------------------")
        print("[SUCESSO] Integração real com Gemini validada com sucesso!\n")
    except Exception as exc:
        print(f"\n[FALHA] Erro durante a extração: {type(exc).__name__}: {exc}\n")
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
