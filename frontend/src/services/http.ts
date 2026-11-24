import { API_BASE_URL, REQUEST_TIMEOUT_MS } from '../config/env';

export type ApiErrorKind = 'network' | 'timeout' | 'http' | 'parse' | 'aborted';

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status?: number;

  constructor(kind: ApiErrorKind, message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.kind = kind;
    this.status = status;
  }
}

interface RequestOptions {
  signal?: AbortSignal;
  timeoutMs?: number;
}

/**
 * GET JSON com timeout, cancelamento e erros tipados.
 * Mensagens de erro são amigáveis e não expõem detalhes internos do servidor.
 */
export async function getJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { signal, timeoutMs = REQUEST_TIMEOUT_MS } = options;
  const controller = new AbortController();
  let timedOut = false;

  const timer = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, timeoutMs);
  const onExternalAbort = () => controller.abort();
  signal?.addEventListener('abort', onExternalAbort, { once: true });

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller.signal,
    });
  } catch {
    if (timedOut) throw new ApiError('timeout', 'A API não respondeu dentro do tempo esperado.');
    if (signal?.aborted) throw new ApiError('aborted', 'Requisição cancelada.');
    throw new ApiError('network', 'Não foi possível conectar à API.');
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', onExternalAbort);
  }

  if (!response.ok) {
    throw new ApiError('http', `A API respondeu com o status ${response.status}.`, response.status);
  }

  try {
    return (await response.json()) as T;
  } catch {
    throw new ApiError('parse', 'A resposta da API não está no formato esperado.');
  }
}
