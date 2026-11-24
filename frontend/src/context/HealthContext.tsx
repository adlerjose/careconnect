import { createContext, useContext, type ReactNode } from 'react';
import { HEALTH_POLL_INTERVAL_MS } from '../config/env';
import { useHealth } from '../hooks/useHealth';
import { HEALTH_ENDPOINTS } from '../services/health';

type HealthContextValue = ReturnType<typeof useHealth>;

const HealthContext = createContext<HealthContextValue | null>(null);

/** Compartilha o estado de GET /api/v1/health entre cabeçalho, dashboard e rodapé. */
export function HealthProvider({ children }: { children: ReactNode }) {
  const health = useHealth(HEALTH_ENDPOINTS.v1, HEALTH_POLL_INTERVAL_MS);
  return <HealthContext.Provider value={health}>{children}</HealthContext.Provider>;
}

export function useApiHealth(): HealthContextValue {
  const ctx = useContext(HealthContext);
  if (!ctx) throw new Error('useApiHealth deve ser usado dentro de <HealthProvider>.');
  return ctx;
}
