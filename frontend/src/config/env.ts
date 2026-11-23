/**
 * Configuração de ambiente do frontend.
 * VITE_API_BASE_URL vazio => caminhos relativos atendidos pelo proxy do Vite.
 */
export const API_BASE_URL: string = (import.meta.env.VITE_API_BASE_URL ?? '').trim().replace(/\/+$/, '');

/** Intervalo de verificação automática da saúde da API (ms). */
export const HEALTH_POLL_INTERVAL_MS = 30_000;

/** Tempo máximo de espera por resposta da API (ms). */
export const REQUEST_TIMEOUT_MS = 8_000;

/** Monta a URL absoluta de um recurso do backend (para links como /docs). */
export function backendUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}
