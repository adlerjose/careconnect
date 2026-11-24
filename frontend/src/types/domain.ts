/**
 * Tipos de domínio espelhando os modelos SQLAlchemy do backend.
 * Usados apenas para estruturar a interface; nenhum endpoint de leitura
 * existe ainda para esses recursos.
 *
 * Campos internos/sensíveis (ex.: Message.raw_payload) foram omitidos de
 * propósito — o frontend não deve exibir payloads brutos.
 */

/** backend/app/modules/patients/models.py */
export interface Patient {
  id: string;
  name: string;
  whatsapp_number: string;
  created_at: string;
}

/** Tipos produzidos por _extract_message em webhook_service.py */
export type MessageType = 'text' | 'audio' | 'unknown';

/** backend/app/modules/messages/models.py (sem raw_payload) */
export interface Message {
  id: string;
  patient_id: string;
  wa_message_id: string | null;
  message_type: MessageType;
  content_text: string | null;
  processed_at: string | null;
  processing_error: string | null;
  created_at: string;
}

/** backend/app/modules/ai/schemas/clinical.py — ClinicalExtractionResult */
export interface ClinicalExtraction {
  symptoms: string[];
  duration: string | null;
  medications: string[];
  clinical_summary: string | null;
  confidence: number | null;
  requires_human_review: boolean;
}

/** backend/app/modules/triage/models.py */
export interface TriageRecord {
  id: string;
  patient_id: string;
  message_id: string;
  clinical_summary: string | null;
  extracted_data: ClinicalExtraction;
  confidence: number | null;
  requires_human_review: boolean;
  created_at: string;
}

export type ProcessingState = 'processed' | 'error' | 'pending';

/** Deriva o estado de processamento a partir dos campos reais da mensagem. */
export function getProcessingState(message: Pick<Message, 'processed_at' | 'processing_error'>): ProcessingState {
  if (message.processing_error) return 'error';
  if (message.processed_at) return 'processed';
  return 'pending';
}
