import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError } from '../services/http';
import { fetchHealth, type HealthCheckResponse, type HealthEndpoint } from '../services/health';

export type HealthStatus = 'loading' | 'online' | 'degraded' | 'offline';

export interface HealthState {
  status: HealthStatus;
  data: HealthCheckResponse | null;
  error: string | null;
  latencyMs: number | null;
  checkedAt: Date | null;
  isRefreshing: boolean;
}

const initialState: HealthState = {
  status: 'loading',
  data: null,
  error: null,
  latencyMs: null,
  checkedAt: null,
  isRefreshing: false,
};

/**
 * Consulta um endpoint de saúde real do backend, com verificação periódica opcional.
 * - online: respondeu 200 com status "ok"
 * - degraded: respondeu, mas com status diferente de "ok"
 * - offline: falha de rede, timeout, HTTP de erro ou contrato inválido
 */
export function useHealth(endpoint: HealthEndpoint, pollMs?: number) {
  const [state, setState] = useState<HealthState>(initialState);
  const controllerRef = useRef<AbortController | null>(null);

  const check = useCallback(async () => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setState((s) => ({ ...s, isRefreshing: true }));

    try {
      const { data, latencyMs } = await fetchHealth(endpoint, controller.signal);
      if (controller.signal.aborted) return;
      setState({
        status: data.status === 'ok' ? 'online' : 'degraded',
        data,
        error: null,
        latencyMs,
        checkedAt: new Date(),
        isRefreshing: false,
      });
    } catch (err) {
      if (err instanceof ApiError && err.kind === 'aborted') return;
      if (controller.signal.aborted) return;
      setState({
        status: 'offline',
        data: null,
        error: err instanceof Error ? err.message : 'Falha desconhecida ao consultar a API.',
        latencyMs: null,
        checkedAt: new Date(),
        isRefreshing: false,
      });
    }
  }, [endpoint]);

  useEffect(() => {
    void check();
    if (!pollMs) return () => controllerRef.current?.abort();
    const id = window.setInterval(() => void check(), pollMs);
    return () => {
      window.clearInterval(id);
      controllerRef.current?.abort();
    };
  }, [check, pollMs]);

  return { ...state, refresh: check };
}
