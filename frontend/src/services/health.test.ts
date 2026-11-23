import { describe, expect, it, vi } from 'vitest';
import { ApiError } from './http';
import { fetchHealth, HEALTH_ENDPOINTS, isHealthCheckResponse } from './health';

const OK = { status: 'ok', app_name: 'CareConnect PI', version: '0.1.0', environment: 'development' };

function mockFetch(impl: () => Promise<Response>) {
  const fn = vi.fn(impl);
  vi.stubGlobal('fetch', fn);
  return fn;
}

describe('isHealthCheckResponse', () => {
  it('aceita o contrato do backend', () => {
    expect(isHealthCheckResponse(OK)).toBe(true);
  });

  it('rejeita respostas fora do contrato', () => {
    expect(isHealthCheckResponse({ status: 'ok' })).toBe(false);
    expect(isHealthCheckResponse(null)).toBe(false);
  });
});

describe('fetchHealth', () => {
  it('consulta somente os endpoints de saúde existentes', async () => {
    const fetchMock = mockFetch(async () => new Response(JSON.stringify(OK), { status: 200 }));
    const result = await fetchHealth(HEALTH_ENDPOINTS.v1);
    expect(result.data).toEqual(OK);
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/health', expect.objectContaining({ method: 'GET' }));
  });

  it('converte erro HTTP em ApiError', async () => {
    mockFetch(async () => new Response('fail', { status: 503 }));
    await expect(fetchHealth(HEALTH_ENDPOINTS.root)).rejects.toMatchObject({ kind: 'http', status: 503 });
  });

  it('converte falha de rede em ApiError', async () => {
    mockFetch(async () => {
      throw new TypeError('Failed to fetch');
    });
    await expect(fetchHealth(HEALTH_ENDPOINTS.root)).rejects.toBeInstanceOf(ApiError);
    await expect(fetchHealth(HEALTH_ENDPOINTS.root)).rejects.toMatchObject({ kind: 'network' });
  });

  it('rejeita resposta com formato inesperado', async () => {
    mockFetch(async () => new Response(JSON.stringify({ foo: 1 }), { status: 200 }));
    await expect(fetchHealth(HEALTH_ENDPOINTS.v1)).rejects.toMatchObject({ kind: 'parse' });
  });
});
