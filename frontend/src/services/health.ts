import { ApiError, getJson } from './http';

/**
 * Contrato de backend/app/api/routes/health.py — HealthCheckResponse.
 * Disponível em GET /health e GET /api/v1/health.
 */
export interface HealthCheckResponse {
  status: string;
  app_name: string;
  version: string;
  environment: string;
}

export const HEALTH_ENDPOINTS = {
  root: '/health',
  v1: '/api/v1/health',
} as const;

export type HealthEndpoint = (typeof HEALTH_ENDPOINTS)[keyof typeof HEALTH_ENDPOINTS];

export function isHealthCheckResponse(value: unknown): value is HealthCheckResponse {
  if (!value || typeof value !== 'object') return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.status === 'string' &&
    typeof v.app_name === 'string' &&
    typeof v.version === 'string' &&
    typeof v.environment === 'string'
  );
}

export interface HealthResult {
  data: HealthCheckResponse;
  latencyMs: number;
}

export async function fetchHealth(endpoint: HealthEndpoint, signal?: AbortSignal): Promise<HealthResult> {
  const startedAt = performance.now();
  const payload = await getJson<unknown>(endpoint, { signal });
  if (!isHealthCheckResponse(payload)) {
    throw new ApiError('parse', 'A resposta de saúde da API não corresponde ao contrato esperado.');
  }
  return { data: payload, latencyMs: Math.round(performance.now() - startedAt) };
}
