"""
Script para execução e validação semântica de áudio real com o Google Gemini.

Utilização:
    python scripts/manual_gemini_audio_test.py [caminho/do/audio.ogg]

Exemplos:
    # 1. Teste com áudio real de relato falado (WhatsApp OGG/Opus, MP3, WAV, etc.):
    python scripts/manual_gemini_audio_test.py sample_relato.ogg

    # 2. Teste padrão demonstrativo com áudio sintético silencioso (quando nenhum arquivo é passado):
    python scripts/manual_gemini_audio_test.py

Requisitos:
    - Definir a chave no arquivo backend/.env (GEMINI_API_KEY="...") ou no terminal:
        export GEMINI_API_KEY="sua_chave"
"""

import asyncio
import io
import os
import struct
import sys
import wave
from pathlib import Path

# Assegura que o diretório 'backend' esteja no sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv

load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / ".env")

from app.core.config import settings
from app.modules.ai.pipelines.extraction_pipeline import ClinicalExtractionPipeline
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.audio_validator import load_audio_from_source, sniff_audio_mime_type
from app.modules.ai.services.gemini_provider import GeminiProvider


def _generate_synthetic_silent_wav() -> bytes:
    """Gera um arquivo WAV sintético de 1.5s (16kHz, mono) com silêncio para testes sem fala."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(struct.pack("<h", 0) * 24000)
    return buf.getvalue()


async def main():
    api_key = os.environ.get("GEMINI_API_KEY") or settings.GEMINI_API_KEY
    if not api_key or not api_key.strip():
        print("\n[ERRO] Variável GEMINI_API_KEY não foi encontrada.")
        print("Preencha a variável GEMINI_API_KEY no arquivo .env ou exporte-a via:")
        print("  export GEMINI_API_KEY='sua_chave'\n")
        sys.exit(1)

    print("==================================================================")
    print("CareConnect PI - Validação de Áudio Clínico (Google Gemini)")
    print("==================================================================")

    provider = GeminiProvider(api_key=api_key)
    print(f"Provedor ativo:      {provider.provider_name}")
    print(f"Modelo configurado:  {provider.model_name}")
    print(f"Timeout configurado: {provider.timeout}s")
    print(f"Chave presente:      {provider.is_configured()}\n")

    audio_bytes: bytes
    detected_mime: str
    source_description: str
    is_real_speech_sample: bool = False

    if len(sys.argv) > 1:
        audio_path = Path(sys.argv[1])
        if not audio_path.exists() or not audio_path.is_file():
            print(f"[ERRO] Arquivo de áudio não encontrado no caminho: '{audio_path}'")
            print("Verifique o caminho do arquivo e tente novamente.")
            sys.exit(1)

        source_description = str(audio_path.name)
        try:
            audio_bytes, detected_mime = load_audio_from_source(audio_path)
            is_real_speech_sample = True
            print(f"[ARQUIVO FORNECIDO]  {audio_path.resolve()}")
        except Exception as exc:
            print(f"[ERRO DE VALIDAÇÃO]  {exc}")
            sys.exit(1)
    else:
        source_description = "audio_sintetico_silencio.wav"
        raw_wav = _generate_synthetic_silent_wav()
        audio_bytes, detected_mime = load_audio_from_source(raw_wav, declared_mime_type="audio/wav")
        is_real_speech_sample = False
        print("[MODO DEMONSTRAÇÃO]  Nenhum arquivo especificado via linha de comando.")
        print("                     Utilizando amostra WAV sintética com silêncio.")
        print("                     Para testar fala real, execute:")
        print("                     python scripts/manual_gemini_audio_test.py caminho/do/audio.ogg\n")

    print(f"Tamanho do áudio:    {len(audio_bytes):,} bytes")
    print(f"MIME type detectado: {detected_mime}\n")

    pipeline = ClinicalExtractionPipeline(provider=provider)

    sample_message = AIMessageInput(
        message_id="manual-audio-test-001",
        patient_id="synthetic-patient-9876",
        message_type=MessageType.AUDIO,
        audio_bytes=audio_bytes,
        mime_type=detected_mime,
        audio_url=source_description,
    )

    print("Enviando áudio ao Gemini para extração clínica multimodal...")

    try:
        result = await pipeline.run(sample_message)
        print("\n------------------------------------------------------------------")
        print("Resultado Estruturado Recebido (ClinicalExtractionResult):")
        print("------------------------------------------------------------------")
        print(f"Sintomas extraídos:       {result.symptoms}")
        print(f"Duração relatada:         {result.duration}")
        print(f"Medicamentos mencionados: {result.medications}")
        print(f"Resumo clínico:           {result.clinical_summary}")
        print(f"Confiança estimada (0-1): {result.confidence}")
        print(f"Revisão humana requerida: {result.requires_human_review}")
        print("------------------------------------------------------------------")

        # Avaliação semântica do resultado obtido
        print("\n[AVALIAÇÃO SEMÂNTICA]")
        if not is_real_speech_sample:
            print("(!) ATENÇÃO: O teste foi executado com áudio sintético sem fala.")
            print(f"    - Resumo clínico: '{result.clinical_summary}'")
            print(f"    - Confiança calibrada: {result.confidence} (esperado 0.0 para áudio inaudível)")
            print("    - A validação semântica com fala real em português brasileiro")
            print("      ainda deve ser realizada fornecendo um arquivo de gravação real:")
            print("      python scripts/manual_gemini_audio_test.py caminho/do/relato_paciente.ogg")
        else:
            if result.symptoms:
                print(f"[SUCESSO] Sintomas detectados com sucesso: {result.symptoms}")
            else:
                print("[AVISO] Nenhum sintoma identificado no áudio fornecido.")
            print(f"    - Resumo clínico: '{result.clinical_summary}'")
            print(f"    - Confiança: {result.confidence}")
            print(f"    - Revisão humana obrigatória garantida: {result.requires_human_review}")

        print("\n[SUCESSO] Processamento de áudio concluído sem erros de infraestrutura!\n")

    except Exception as exc:
        print(f"\n[FALHA] Erro durante o processamento de áudio: {type(exc).__name__}: {exc}\n")
    finally:
        await provider.close()


if __name__ == "__main__":
    asyncio.run(main())
