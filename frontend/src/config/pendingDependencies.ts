/**
 * Registro de dependências técnicas: recursos que a interface prevê,
 * mas que ainda NÃO existem na API do backend (branch develop).
 *
 * Os caminhos abaixo correspondem aos pontos de extensão comentados em
 * backend/app/api/routes/__init__.py. Eles NÃO são chamados pelo frontend;
 * servem apenas para sinalizar claramente na interface o que está pendente.
 */
export type PendingResource = 'patients' | 'patientDetail' | 'messages' | 'triage';

export interface PendingDependency {
  resource: PendingResource;
  label: string;
  plannedPath: string;
  description: string;
}

export const PENDING_DEPENDENCIES: Record<PendingResource, PendingDependency> = {
  patients: {
    resource: 'patients',
    label: 'Listagem de pacientes',
    plannedPath: 'GET /api/v1/patients',
    description: 'Endpoint de leitura de pacientes ainda não implementado no backend.',
  },
  patientDetail: {
    resource: 'patientDetail',
    label: 'Detalhes do paciente',
    plannedPath: 'GET /api/v1/patients/{id}',
    description: 'Consulta individual de paciente, mensagens e triagens ainda não disponível.',
  },
  messages: {
    resource: 'messages',
    label: 'Consulta de mensagens',
    plannedPath: 'GET /api/v1/messages',
    description: 'O webhook apenas recebe eventos; não há endpoint de consulta de mensagens.',
  },
  triage: {
    resource: 'triage',
    label: 'Registros de triagem',
    plannedPath: 'GET /api/v1/triage',
    description: 'Registros de triagem são gravados no banco, mas não há endpoint de leitura.',
  },
};
