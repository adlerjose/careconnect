import pytest
from pydantic import ValidationError
from app.modules.ai.schemas.clinical import ClinicalExtractionResult


def test_valid_clinical_extraction_full():
    """Valida a criação completa do resultado de extração clínica com dados sintéticos."""
    result = ClinicalExtractionResult(
        symptoms=["cefaleia", "náusea"],
        duration="48 horas",
        medications=["paracetamol 750mg"],
        clinical_summary="Paciente sintético relata cefaleia e náusea há 48 horas.",
        confidence=0.88,
        requires_human_review=False,
    )

    assert result.symptoms == ["cefaleia", "náusea"]
    assert result.duration == "48 horas"
    assert result.medications == ["paracetamol 750mg"]
    assert result.confidence == 0.88
    assert result.requires_human_review is False


def test_optional_fields_and_defaults():
    """Valida comportamento conservador com valores padrão e ausência de informações."""
    result = ClinicalExtractionResult()

    assert result.symptoms == []
    assert result.duration is None
    assert result.medications == []
    assert result.clinical_summary is None
    assert result.confidence is None
    assert result.requires_human_review is False


def test_confidence_boundary_validations():
    """Valida que o campo confidence aceita estritamente o intervalo [0.0, 1.0]."""
    # Limites válidos
    res_min = ClinicalExtractionResult(confidence=0.0)
    assert res_min.confidence == 0.0

    res_max = ClinicalExtractionResult(confidence=1.0)
    assert res_max.confidence == 1.0

    res_mid = ClinicalExtractionResult(confidence=0.5)
    assert res_mid.confidence == 0.5

    # Valores fora dos limites devem falhar
    with pytest.raises(ValidationError):
        ClinicalExtractionResult(confidence=-0.01)

    with pytest.raises(ValidationError):
        ClinicalExtractionResult(confidence=1.01)

    with pytest.raises(ValidationError):
        ClinicalExtractionResult(confidence=2.0)


def test_clean_string_lists_and_empty_duration():
    """Verifica sanitização de listas (remoção de vazios e duplicatas) e tratamento de duração vazia."""
    result = ClinicalExtractionResult(
        symptoms=["  tosse  ", "", "febre", "tosse", "   "],
        medications=["  ibuprofeno  ", "ibuprofeno", ""],
        duration="   ",
    )

    # Não deve conter vazios nem duplicatas
    assert result.symptoms == ["tosse", "febre"]
    assert result.medications == ["ibuprofeno"]
    # Espaços em branco devem ser convertidos para None (informação ausente)
    assert result.duration is None


def test_requires_human_review_flag():
    """Valida atribuição explícita de necessidade de revisão humana para casos ambíguos."""
    result = ClinicalExtractionResult(
        symptoms=["dor indeterminada"],
        requires_human_review=True,
    )
    assert result.requires_human_review is True


def test_extra_fields_forbidden_in_clinical_result():
    """Garante que atributos diagnósticos ou não mapeados sejam rejeitados."""
    with pytest.raises(ValidationError):
        ClinicalExtractionResult(
            symptoms=["dor"],
            diagnostico_provisorio="Invalido",  # type: ignore
        )
