from typing import Optional
from app.core.logging import get_logger
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import AIModuleError
from app.modules.ai.services.gemini_provider import GeminiProvider

logger = get_logger("careconnect.ai.pipeline")


class ClinicalExtractionPipeline:
    """
    Pipeline de orquestração para extração de dados clínicos a partir de mensagens recebidas.
    
    Recebe um contrato de entrada AIMessageInput e delega o processamento ao provedor
    de IA configurado (respeitando se o conteúdo é texto ou áudio).
    """

    def __init__(self, provider: Optional[BaseAIProvider] = None) -> None:
        """
        Inicializa o pipeline com um provedor de IA injetado.
        Por padrão, utiliza o GeminiProvider caso nenhum seja fornecido.
        """
        self.provider = provider or GeminiProvider()

    async def run(self, message: AIMessageInput) -> ClinicalExtractionResult:
        """
        Executa o pipeline de extração clínica para a mensagem informada.
        
        :param message: Instância validada de AIMessageInput.
        :return: ClinicalExtractionResult com os dados estruturados extraídos.
        """
        logger.info(
            f"Iniciando pipeline de extração [message_id={message.message_id}, "
            f"type={message.message_type}, provider={self.provider.provider_name}]"
        )

        try:
            if message.message_type == MessageType.TEXT:
                result = await self.provider.process_text(text=message)
            elif message.message_type == MessageType.AUDIO:
                import inspect
                sig = inspect.signature(self.provider.process_audio)
                if "audio" in sig.parameters:
                    result = await self.provider.process_audio(audio=message)
                else:
                    result = await self.provider.process_audio(audio_url=message.audio_url or "")
            else:
                raise AIModuleError(f"Tipo de mensagem não suportado: {message.message_type}")

            logger.info(
                f"Extração concluída com sucesso [message_id={message.message_id}, "
                f"symptoms_count={len(result.symptoms)}, requires_review={result.requires_human_review}]"
            )
            return result

        except Exception as exc:
            # Tratamento conservador: registra a ocorrência sem expor dados clínicos sensíveis
            logger.error(
                f"Falha no processamento da mensagem [message_id={message.message_id}]: {type(exc).__name__}"
            )
            raise
