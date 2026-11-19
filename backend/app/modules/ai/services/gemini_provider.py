import asyncio
import socket
from typing import Optional, Union
from google import genai
from google.genai import errors, types
import httpx
from pydantic import ValidationError

from app.core.config import settings
from app.core.logging import get_logger
from app.modules.ai.prompts.templates import SYSTEM_CLINICAL_EXTRACTION_PROMPT
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import (
    AIExtractionError,
    AIModuleError,
    AIProviderAuthenticationError,
    AIProviderBlockedError,
    AIProviderError,
    AIProviderNotConfiguredError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)

logger = get_logger("careconnect.ai.gemini")


def _ensure_ipv4_priority() -> None:
    """
    Garante que conexões socket priorizem IPv4 caso o sistema Linux local
    possua pilha IPv6 habilitada mas sem rota externa funcional para a Internet.
    """
    if getattr(socket, "_ipv4_priority_configured", False):
        return

    _orig_getaddrinfo = socket.getaddrinfo

    def _ipv4_first_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if family == socket.AF_UNSPEC:
            try:
                res = _orig_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)
                if res:
                    return res
            except socket.gaierror:
                pass
        return _orig_getaddrinfo(host, port, family, type, proto, flags)

    socket.getaddrinfo = _ipv4_first_getaddrinfo
    socket._ipv4_priority_configured = True


_ensure_ipv4_priority()


class GeminiProvider(BaseAIProvider):
    """
    Provedor de Inteligência Artificial baseado no Google Gemini Developer API
    utilizando o SDK oficial 'google-genai' de forma assíncrona.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> None:
        """
        Inicializa o provedor Gemini utilizando as configurações da aplicação.
        """
        self._api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL
        self._timeout = float(timeout if timeout is not None else settings.GEMINI_TIMEOUT)
        self._client: Optional[genai.Client] = None

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def timeout(self) -> float:
        return self._timeout

    def is_configured(self) -> bool:
        """Verifica se há chave de API informada nas configurações."""
        return bool(self._api_key and self._api_key.strip())

    def _get_client(self) -> genai.Client:
        """
        Retorna uma instância única reutilizável do cliente Gemini.
        Levanta AIProviderNotConfiguredError caso a API Key não esteja presente.
        """
        if not self.is_configured():
            raise AIProviderNotConfiguredError(
                "O provedor Gemini não está configurado. A variável GEMINI_API_KEY não foi definida."
            )

        if self._client is None:
            # O SDK google-genai interpreta HttpOptions.timeout em milissegundos
            timeout_ms = float(self._timeout * 1000.0)
            http_options = types.HttpOptions(timeout=timeout_ms)
            self._client = genai.Client(
                api_key=self._api_key,
                http_options=http_options,
            )
        return self._client

    def _handle_api_error(self, exc: errors.APIError) -> None:
        """
        Mapeia códigos de status HTTP da API Gemini para exceções de domínio do sistema.
        """
        status_code = getattr(exc, "code", None)
        logger.error(f"Erro reportado pela API Google Gemini: status_code={status_code}")

        if status_code in (401, 403):
            raise AIProviderAuthenticationError(
                "Falha de autenticação com o provedor Gemini. Verifique a chave de API configurada."
            ) from exc
        elif status_code == 429:
            raise AIProviderRateLimitError(
                "Limite de requisições ou cota de consumo excedida na API do Google Gemini."
            ) from exc
        elif status_code in (500, 502, 503, 504):
            detail = "modelo temporariamente sob alta demanda na infraestrutura da Google" if status_code == 503 else "serviço indisponível"
            raise AIProviderUnavailableError(
                f"Serviço do Google Gemini temporariamente indisponível ({status_code}: {detail}). Tente novamente em instantes."
            ) from exc
        else:
            raise AIProviderError(
                f"Falha de comunicação com a API do Google Gemini (código {status_code})."
            ) from exc

    async def process_text(self, text: Union[AIMessageInput, str]) -> ClinicalExtractionResult:
        """
        Processa um conteúdo textual ou contrato AIMessageInput e extrai as informações
        clínicas estruturadas através do Google Gemini.
        
        Garantias de Privacidade e Segurança:
        - NÃO envia patient_id ou message_id ao modelo.
        - Não registra conteúdo clínico nem credenciais nos logs.
        - Força requires_human_review=True em todas as extrações do MVP.
        """
        if isinstance(text, AIMessageInput):
            if text.message_type != MessageType.TEXT:
                raise AIModuleError(
                    f"Tipo de mensagem inválido para processamento textual: {text.message_type}. Esperado TEXT."
                )
            raw_content = text.content
        elif isinstance(text, str):
            raw_content = text
        else:
            raise AIModuleError(
                f"Entrada inválida para process_text: esperado AIMessageInput ou str, recebido {type(text).__name__}."
            )

        if not raw_content or not str(raw_content).strip():
            raise AIExtractionError("Conteúdo textual vazio para extração clínica.")

        content_to_send = str(raw_content).strip()
        client = self._get_client()

        # Configuração de Saída Estruturada usando o schema Pydantic oficial
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_CLINICAL_EXTRACTION_PROMPT,
            response_mime_type="application/json",
            response_schema=ClinicalExtractionResult,
            temperature=0.0,
        )

        logger.info(f"Enviando solicitação de extração textual ao modelo Gemini [{self._model_name}]")

        try:
            response = await asyncio.wait_for(
                client.aio.models.generate_content(
                    model=self._model_name,
                    contents=content_to_send,
                    config=config,
                ),
                timeout=self._timeout,
            )
        except (asyncio.TimeoutError, httpx.TimeoutException) as exc:
            logger.error(f"Timeout de {self._timeout}s excedido na chamada ao Gemini [{self._model_name}]")
            raise AIProviderTimeoutError(
                f"Tempo limite de {self._timeout}s excedido na chamada à API do Gemini."
            ) from exc
        except errors.APIError as exc:
            self._handle_api_error(exc)
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error(f"Erro inesperado no cliente Gemini: {type(exc).__name__}")
            raise AIProviderError(f"Falha de comunicação com o provedor Gemini: {type(exc).__name__}") from exc

        # Verificação de bloqueios de segurança nas respostas geradas
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            finish_reason = getattr(candidate, "finish_reason", None)
            if finish_reason and finish_reason in (
                types.FinishReason.SAFETY,
                types.FinishReason.BLOCKLIST,
                types.FinishReason.PROHIBITED_CONTENT,
                types.FinishReason.SPII,
            ):
                logger.warning(f"Resposta do modelo bloqueada por política de segurança: finish_reason={finish_reason}")
                raise AIProviderBlockedError("A resposta do modelo foi bloqueada por políticas de segurança.")

        response_text = getattr(response, "text", None)
        if not response_text or not response_text.strip():
            raise AIExtractionError("O modelo Gemini retornou uma resposta textual vazia.")

        # Validação da saída com Pydantic
        try:
            if hasattr(response, "parsed") and isinstance(response.parsed, ClinicalExtractionResult):
                extraction_result = response.parsed
            else:
                extraction_result = ClinicalExtractionResult.model_validate_json(response_text)
        except ValidationError as exc:
            logger.error("Falha de validação Pydantic no JSON retornado pelo Gemini")
            raise AIExtractionError("A resposta estruturada do Gemini não atende ao schema ClinicalExtractionResult.") from exc
        except Exception as exc:
            logger.error(f"Erro ao decodificar JSON retornado pelo Gemini: {type(exc).__name__}")
            raise AIExtractionError("Formato de resposta retornado pelo Gemini é inválido.") from exc

        # Regra de Segurança do MVP: toda extração requer revisão humana obrigatória
        extraction_result = extraction_result.model_copy(update={"requires_human_review": True})

        logger.info(
            f"Extração concluída com sucesso pelo Gemini [symptoms_count={len(extraction_result.symptoms)}, "
            f"confidence={extraction_result.confidence}, requires_human_review={extraction_result.requires_human_review}]"
        )
        return extraction_result

    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        """
        Processamento multimodal de áudio via Gemini (preparado para tarefas posteriores).
        """
        raise NotImplementedError(
            "O processamento multimodal de áudio via Gemini ainda não está ativo nesta versão do MVP."
        )

    async def close(self) -> None:
        """Encerra recursos de conexão do cliente caso aplicável."""
        self._client = None
