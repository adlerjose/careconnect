import { useApiHealth } from '../context/HealthContext';
import type { HealthStatus } from '../hooks/useHealth';

const LABELS: Record<HealthStatus, string> = {
  loading: 'Verificando API',
  online: 'API online',
  degraded: 'API instável',
  offline: 'API indisponível',
};

/** Pílula de status real, baseada em GET /api/v1/health. */
export function ApiStatusPill() {
  const { status, error } = useApiHealth();
  return (
    <span
      className={`api-pill api-pill--${status}`}
      role="status"
      aria-live="polite"
      title={status === 'offline' && error ? error : 'Fonte: GET /api/v1/health'}
    >
      <span className="api-pill__dot" aria-hidden="true" />
      {LABELS[status]}
    </span>
  );
}

export { LABELS as HEALTH_LABELS };
