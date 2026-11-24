import { Card, CardHeader } from '../components/Card';
import { HEALTH_LABELS } from '../components/ApiStatusPill';
import { Icon } from '../components/Icon';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge, type StatusTone } from '../components/Tag';
import { PENDING_DEPENDENCIES } from '../config/pendingDependencies';
import { backendUrl } from '../config/env';
import { useApiHealth } from '../context/HealthContext';
import { useHealth, type HealthStatus } from '../hooks/useHealth';
import { HEALTH_ENDPOINTS, type HealthEndpoint } from '../services/health';
import { formatEnvironment, formatTime } from '../utils/format';

const TONE: Record<HealthStatus, StatusTone> = {
  loading: 'neutral',
  online: 'success',
  degraded: 'warning',
  offline: 'danger',
};

function EndpointRow({
  endpoint,
  description,
  health,
}: {
  endpoint: HealthEndpoint;
  description: string;
  health: ReturnType<typeof useHealth>;
}) {
  return (
    <li className="endpoint-row">
      <div className="endpoint-row__main">
        <code className="t-mono">GET {endpoint}</code>
        <p className="t-small t-muted">{description}</p>
      </div>
      <div className="endpoint-row__meta">
        <StatusBadge tone={TONE[health.status]}>{HEALTH_LABELS[health.status]}</StatusBadge>
        <span className="t-small t-muted">
          {health.latencyMs !== null ? `${health.latencyMs} ms · ` : ''}
          {formatTime(health.checkedAt)}
        </span>
      </div>
      <button
        type="button"
        className="icon-button"
        onClick={() => void health.refresh()}
        disabled={health.isRefreshing}
        aria-label={`Verificar ${endpoint} novamente`}
      >
        <Icon name="refresh" className={health.isRefreshing ? 'spin' : undefined} />
      </button>
    </li>
  );
}

export function SystemPage() {
  const v1 = useApiHealth();
  const root = useHealth(HEALTH_ENDPOINTS.root);
  const info = v1.data ?? root.data;

  return (
    <>
      <PageHeader
        eyebrow="Sistema"
        title="Estado da"
        accent="integração"
        description="Endpoints realmente disponíveis no backend e dependências técnicas que ainda impedem a exibição de dados."
      />

      <section className="section grid" aria-label="Endpoints disponíveis">
        <div className="col-md-8 col-lg-8">
          <Card padding="lg" className="h-full">
            <CardHeader
              title="Endpoints de saúde"
              description="Consultados em tempo real pelo frontend. Únicos endpoints de leitura existentes."
            />
            <ul className="endpoint-list">
              <EndpointRow endpoint={HEALTH_ENDPOINTS.v1} description="Health check versionado (verificado a cada 30 s)." health={v1} />
              <EndpointRow endpoint={HEALTH_ENDPOINTS.root} description="Health check raiz para monitoramento." health={root} />
            </ul>
          </Card>
        </div>
        <div className="col-md-8 col-lg-4">
          <Card tone="glow" padding="lg" className="h-full stack">
            <span className="t-label t-accent">Aplicação</span>
            <dl className="field-list">
              <div className="field-list__row">
                <dt className="t-label t-muted">Nome</dt>
                <dd>{info?.app_name ?? '—'}</dd>
              </div>
              <div className="field-list__row">
                <dt className="t-label t-muted">Versão</dt>
                <dd>{info?.version ?? '—'}</dd>
              </div>
              <div className="field-list__row">
                <dt className="t-label t-muted">Ambiente</dt>
                <dd>{formatEnvironment(info?.environment)}</dd>
              </div>
            </dl>
            <a className="button button--ink" href={backendUrl('/docs')} target="_blank" rel="noreferrer">
              Documentação da API <Icon name="arrowUpRight" size={16} />
            </a>
          </Card>
        </div>
      </section>

      <section className="section grid" aria-label="Outras integrações">
        <div className="col-md-8 col-lg-6">
          <Card padding="lg" className="h-full">
            <CardHeader title="Recebimento de mensagens" titleAs="h2" />
            <ul className="endpoint-list">
              <li className="endpoint-row endpoint-row--static">
                <div className="endpoint-row__main">
                  <code className="t-mono">POST /webhook/whatsapp</code>
                  <p className="t-small t-muted">
                    Recebe eventos da Evolution API, protegido por chave. É de uso exclusivo da integração com o WhatsApp e
                    não é chamado pelo frontend.
                  </p>
                </div>
                <StatusBadge tone="neutral">Somente entrada</StatusBadge>
              </li>
            </ul>
          </Card>
        </div>
        <div className="col-md-8 col-lg-6">
          <Card padding="lg" className="h-full">
            <CardHeader title="Pendências técnicas" description="Endpoints necessários para conectar as demais telas." titleAs="h2" />
            <ul className="endpoint-list">
              {Object.values(PENDING_DEPENDENCIES).map((d) => (
                <li key={d.resource} className="endpoint-row endpoint-row--static">
                  <div className="endpoint-row__main">
                    <code className="t-mono">{d.plannedPath}</code>
                    <p className="t-small t-muted">{d.label}</p>
                  </div>
                  <StatusBadge tone="warning">Não implementado</StatusBadge>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>
    </>
  );
}
