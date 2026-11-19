"""
Validador e utilitário de inspeção de arquivos de áudio para o módulo de IA.

Responsabilidades:
- Identificação de MIME types via magic bytes e assinaturas de cabeçalho.
- Validação de formatos compatíveis com a API Google Gemini (OGG, MP3, WAV, M4A, AAC, FLAC).
- Aplicação de limites de tamanho (máximo de 20MB para o MVP).
- Rejeição de arquivos vazios, corrompidos ou não sonoros.
- Prevenção ativa de vulnerabilidades SSRF (Server-Side Request Forgery).
"""

from pathlib import Path
from typing import Optional, Set, Tuple, Union
from app.modules.ai.services.exceptions import AIExtractionError

# Limite máximo de tamanho para envio inline à API Gemini no MVP (20 MB)
MAX_AUDIO_SIZE_BYTES: int = 20 * 1024 * 1024
MAX_AUDIO_SIZE_MB: int = 20

# Mapeamento de formatos aceitos e suas variações de MIME type
SUPPORTED_MIME_TYPES: Set[str] = {
    "audio/ogg",
    "audio/opus",
    "audio/x-opus+ogg",
    "audio/mp3",
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/wave",
    "audio/m4a",
    "audio/mp4",
    "audio/x-m4a",
    "audio/aac",
    "audio/x-aac",
    "audio/flac",
    "audio/x-flac",
}

# Normalização de MIME types para conformidade estrita com a API do Google Gemini
NORMALIZED_MIME_MAP = {
    "audio/ogg": "audio/ogg",
    "audio/opus": "audio/ogg",
    "audio/x-opus+ogg": "audio/ogg",
    "audio/mp3": "audio/mp3",
    "audio/mpeg": "audio/mp3",
    "audio/wav": "audio/wav",
    "audio/x-wav": "audio/wav",
    "audio/wave": "audio/wav",
    "audio/m4a": "audio/m4a",
    "audio/mp4": "audio/mp4",
    "audio/x-m4a": "audio/m4a",
    "audio/aac": "audio/aac",
    "audio/x-aac": "audio/aac",
    "audio/flac": "audio/flac",
    "audio/x-flac": "audio/flac",
}

# Assinaturas conhecidas de arquivos NÃO-ÁUDIO para rejeição rápida de dados corrompidos
NON_AUDIO_MAGIC_SIGNATURES = [
    b"%PDF",              # PDF
    b"\x89PNG\r\n\x1a\n", # PNG
    b"\xff\xd8\xff",      # JPEG
    b"GIF8",              # GIF
    b"PK\x03\x04",        # ZIP / DOCX
    b"<!DOCTYPE",         # HTML
    b"<html",             # HTML
    b"{\"",                # JSON
]


def sniff_audio_mime_type(data: bytes) -> Optional[str]:
    """
    Identifica o MIME type de um fluxo de bytes inspecionando seus magic bytes iniciais.
    Não confia na extensão do arquivo.
    """
    if len(data) < 4:
        return None

    # OGG / Opus (comum em mensagens de áudio do WhatsApp)
    if data.startswith(b"OggS"):
        return "audio/ogg"

    # WAV (cabeçalho RIFF com formato WAVE nos bytes 8..12)
    if data.startswith(b"RIFF") and len(data) >= 12 and data[8:12] == b"WAVE":
        return "audio/wav"

    # FLAC
    if data.startswith(b"fLaC"):
        return "audio/flac"

    # MP3 (com tag ID3v2)
    if data.startswith(b"ID3"):
        return "audio/mp3"

    # MP3 raw frames (sync bits 11111111 111xxxxx)
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xE0) == 0xE0:
        return "audio/mp3"

    # M4A / MP4 container (ftyp at offset 4..8)
    if len(data) >= 8 and data[4:8] == b"ftyp":
        brand = data[8:12] if len(data) >= 12 else b""
        if brand in (b"M4A ", b"M4B ", b"M4P "):
            return "audio/m4a"
        return "audio/mp4"

    # AAC ADTS syncword (0xFFF ou 0xFFF1/0xFFF9)
    if len(data) >= 2 and data[0] == 0xFF and (data[1] & 0xF6) == 0xF0:
        return "audio/aac"

    return None


def validate_and_prepare_audio(
    data: bytes,
    declared_mime_type: Optional[str] = None,
    source_reference: Optional[str] = None,
) -> Tuple[bytes, str]:
    """
    Valida e normaliza os dados de áudio para envio à API do Google Gemini.

    :param data: Bytes brutos do áudio.
    :param declared_mime_type: MIME type informado pelo cliente/backend (se houver).
    :param source_reference: Referência textual de origem (usada apenas para contexto de erro).
    :return: Tupla com (bytes_validados, mime_type_normalizado).
    :raises AIExtractionError: Se o áudio for vazio, exceder o tamanho máximo, for corrompido
                               ou tiver formato não suportado.
    """
    if not data or len(data) == 0:
        raise AIExtractionError("Arquivo de áudio vazio. Nenhum dado sonoro foi fornecido para processamento.")

    if len(data) > MAX_AUDIO_SIZE_BYTES:
        size_mb = len(data) / (1024 * 1024)
        raise AIExtractionError(
            f"Arquivo de áudio excede o limite máximo permitido de {MAX_AUDIO_SIZE_MB}MB "
            f"(tamanho recebido: {size_mb:.2f}MB)."
        )

    # Rejeição imediata se coincidir com assinaturas de arquivos não-áudio
    for sig in NON_AUDIO_MAGIC_SIGNATURES:
        if data.startswith(sig):
            raise AIExtractionError(
                "O arquivo fornecido não é um áudio válido (assinatura incompatível ou arquivo corrompido)."
            )

    # Identificação por magic bytes
    sniffed_mime = sniff_audio_mime_type(data)

    target_mime: Optional[str] = None

    if sniffed_mime:
        # Se os magic bytes identificaram o formato, utilizamos o identificado
        target_mime = sniffed_mime
    elif declared_mime_type:
        clean_declared = declared_mime_type.strip().lower()
        if clean_declared in SUPPORTED_MIME_TYPES:
            target_mime = clean_declared

    if not target_mime or target_mime not in NORMALIZED_MIME_MAP:
        ref_info = f" '{source_reference}'" if source_reference else ""
        raise AIExtractionError(
            f"Formato de áudio{ref_info} não suportado ou arquivo corrompido. "
            "Formatos aceitos pelo módulo de IA: OGG/Opus, MP3, WAV, M4A, AAC, FLAC."
        )

    normalized_mime = NORMALIZED_MIME_MAP[target_mime]
    return data, normalized_mime


def load_audio_from_source(
    audio_source: Union[bytes, str, Path],
    declared_mime_type: Optional[str] = None,
) -> Tuple[bytes, str]:
    """
    Carrega e valida o áudio a partir de bytes em memória ou caminho de arquivo local seguro.
    Bloqueia ativamente tentativas de download de URLs remotas (prevenção contra SSRF).

    :param audio_source: Bytes em memória ou caminho de arquivo local (str ou Path).
    :param declared_mime_type: MIME type informado opcionalmente.
    :return: Tupla com (bytes_do_audio, mime_type_normalizado).
    :raises AIExtractionError: Em caso de falha de leitura, SSRF ou validação inválida.
    """
    if isinstance(audio_source, bytes):
        return validate_and_prepare_audio(audio_source, declared_mime_type)

    source_str = str(audio_source).strip()

    # Bloqueio estrito de SSRF para URLs remotas
    if source_str.lower().startswith(("http://", "https://", "ftp://")):
        raise AIExtractionError(
            "Downloads diretos de URLs remotas pelo provedor de IA não são permitidos por segurança (prevenção contra SSRF). "
            "O backend deve efetuar o download seguro e repassar os bytes do áudio validados via 'audio_bytes'."
        )

    file_path = Path(source_str)
    if not file_path.exists() or not file_path.is_file():
        raise AIExtractionError(f"Arquivo de áudio local não encontrado: '{source_str}'.")

    try:
        raw_bytes = file_path.read_bytes()
    except Exception as exc:
        raise AIExtractionError(f"Falha ao ler o arquivo de áudio local: {type(exc).__name__}") from exc

    return validate_and_prepare_audio(raw_bytes, declared_mime_type, source_reference=source_str)
