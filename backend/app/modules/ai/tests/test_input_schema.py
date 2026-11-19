import pytest
from pydantic import ValidationError
from app.modules.ai.schemas.input import AIMessageInput, MessageType


def test_valid_text_message_input():
    """Valida a criação correta de uma mensagem do tipo TEXT com dados sintéticos."""
    message = AIMessageInput(
        message_id="msg-synth-001",
        patient_id="patient-synth-001",
        message_type=MessageType.TEXT,
        content="Sinto dor nas costas há três dias e tomei analgésico.",
    )

    assert message.message_id == "msg-synth-001"
    assert message.patient_id == "patient-synth-001"
    assert message.message_type == MessageType.TEXT
    assert message.content == "Sinto dor nas costas há três dias e tomei analgésico."
    assert message.audio_url is None


def test_valid_audio_message_input():
    """Valida a criação correta de uma mensagem do tipo AUDIO com áudio referenciado."""
    message = AIMessageInput(
        message_id="msg-synth-002",
        patient_id="patient-synth-002",
        message_type=MessageType.AUDIO,
        audio_url="https://storage.local/audios/audio-synth-002.ogg",
    )

    assert message.message_id == "msg-synth-002"
    assert message.patient_id == "patient-synth-002"
    assert message.message_type == MessageType.AUDIO
    assert message.audio_url == "https://storage.local/audios/audio-synth-002.ogg"
    assert message.content is None


def test_text_message_requires_content():
    """Garante que mensagens do tipo TEXT falhem se 'content' for omitido ou vazio."""
    with pytest.raises(ValidationError) as exc_info:
        AIMessageInput(
            message_id="msg-synth-003",
            patient_id="patient-synth-003",
            message_type=MessageType.TEXT,
            content=None,
        )
    assert "Mensagens do tipo TEXT exigem o preenchimento obrigatório" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AIMessageInput(
            message_id="msg-synth-003",
            patient_id="patient-synth-003",
            message_type=MessageType.TEXT,
            content="   ",
        )
    assert "Mensagens do tipo TEXT exigem o preenchimento obrigatório" in str(exc_info.value)


def test_audio_message_requires_audio_url():
    """Garante que mensagens do tipo AUDIO falhem se 'audio_url' for omitido ou vazio."""
    with pytest.raises(ValidationError) as exc_info:
        AIMessageInput(
            message_id="msg-synth-004",
            patient_id="patient-synth-004",
            message_type=MessageType.AUDIO,
            audio_url=None,
        )
    assert "Mensagens do tipo AUDIO exigem o preenchimento obrigatório" in str(exc_info.value)

    with pytest.raises(ValidationError) as exc_info:
        AIMessageInput(
            message_id="msg-synth-004",
            patient_id="patient-synth-004",
            message_type=MessageType.AUDIO,
            audio_url="   ",
        )
    assert "Mensagens do tipo AUDIO exigem o preenchimento obrigatório" in str(exc_info.value)


def test_invalid_message_type_rejected():
    """Verifica que tipos de mensagem desconhecidos são rejeitados."""
    with pytest.raises(ValidationError):
        AIMessageInput(
            message_id="msg-synth-005",
            patient_id="patient-synth-005",
            message_type="VIDEO",  # type: ignore
            content="Conteúdo de vídeo não suportado",
        )


def test_blank_identifiers_rejected():
    """Verifica que identificadores vazios ou com apenas espaços em branco são rejeitados."""
    with pytest.raises(ValidationError):
        AIMessageInput(
            message_id="   ",
            patient_id="patient-synth-006",
            message_type=MessageType.TEXT,
            content="Relato sintético",
        )

    with pytest.raises(ValidationError):
        AIMessageInput(
            message_id="msg-synth-007",
            patient_id="",
            message_type=MessageType.TEXT,
            content="Relato sintético",
        )


def test_extra_fields_forbidden():
    """Garante que campos não previstos no contrato de entrada sejam rejeitados."""
    with pytest.raises(ValidationError):
        AIMessageInput(
            message_id="msg-synth-008",
            patient_id="patient-synth-008",
            message_type=MessageType.TEXT,
            content="Relato sintético",
            campo_desconhecido="valor_invalido",  # type: ignore
        )
