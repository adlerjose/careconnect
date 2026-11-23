import { Link } from 'react-router-dom';
import { Card, CardHeader } from '../components/Card';
import { ClinicalDisclaimer } from '../components/ClinicalDisclaimer';
import { EmptyState } from '../components/EmptyState';
import { FlowDiagram } from '../components/FlowDiagram';
import { Icon } from '../components/Icon';
import { PageHeader } from '../components/PageHeader';
import { PendingNotice } from '../components/PendingNotice';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/Tag';
import { HEALTH_LABELS } from '../components/ApiStatusPill';
import { useApiHealth } from '../context/HealthContext';
import { formatEnvironment, formatTime } from '../utils/format';

function ApiHealthCard() {
  const { status, data, error, latencyMs, checkedAt, isRefreshing, refresh } = useApiHealth();
  const tone = status === 'online' ? 'success' : status === 'offline' ? 'danger' : status === 'degraded' ? 'warning' : 'neutral';

  return (
    <Card tone="ink" padding="lg" className="health-card" aria-live="polite">
      <div className="health-card__top">
        <span className="t-label health-card__eyebrow">Conexão com o backend</span>
        <button
          type="button"
          className="icon-button icon-button--on-dark"
          onClick={() => void refresh()}
          disabled={isRefreshing}
          aria-label="Verificar novamente"
        >
          <Icon name="refresh" className={isRefreshing ? 'spin' : undefined} />
        </button>
      </div>

      <div className="stack stack--sm">
        <p className="t-card-title">{HEALTH_LABELS[status]}</p>
        <div>
          <StatusBadge tone={tone}>
            {status === 'loading' ? 'Consultando…' : status === 'online' ? 'Operacional' : status === 'degraded' ? 'Resposta inesperada' : 'Sem resposta'}
          </StatusBadge>
        </div>
      </div>

      {status === 'offline' && (
        <p className="t-small health-card__error">
          {error} Verifique se o backend está em execução em <code className="t-mono">localhost:8000</code>.
        </p>
      )}

      <dl className="health-card__meta">
        <div>
          <dt className="t-label">Versão</dt>
          <dd>{data?.version ?? '—'}</dd>
        </div>
        <div>
          <dt className="t-label">Ambiente</dt>
          <dd>{formatEnvironment(data?.environment)}</dd>
        </div>
        <div>
          <dt className="t-label">Latência</dt>
          <dd>{latencyMs !== null ? `${latencyMs} ms` : '—'}</dd>
        </div>
        <div>
          <dt className="t-label">Verificado</dt>
          <dd>{formatTime(checkedAt)}</dd>
        </div>
      </dl>

      <p className="t-label health-card__source">Fonte: GET /api/v1/health · atualização a cada 30 s</p>
    </Card>
  );
}

export function DashboardPage() {
  return (
    <>
      <PageHeader
        eyebrow="Painel"
        title="Acompanhamento pós-atendimento,"
        accent="com revisão humana"
        description="O CareConnect recebe relatos de pacientes pelo WhatsApp, organiza as informações com apoio de IA e sinaliza o que precisa da atenção de um profissional de saúde."
      />

      <section className="section grid" aria-labelledby="indicadores">
        <h2 id="indicadores" className="sr-only">
          Indicadores
        </h2>
        <div className="col-md-4 col-lg-3">
          <StatCard label="Pacientes" icon="users" value={null} />
        </div>
        <div className="col-md-4 col-lg-3">
          <StatCard label="Mensagens recebidas" icon="message" value={null} />
        </div>
        <div className="col-md-4 col-lg-3">
          <StatCard label="Triagens registradas" icon="pulse" value={null} />
        </div>
        <div className="col-md-4 col-lg-3">
          <StatCard label="Aguardando revisão humana" icon="shield" value={null} />
        </div>
        <div className="col-lg-12">
          <PendingNotice resources={['patients', 'messages', 'triage']} />
        </div>
      </section>

      <section className="section grid" aria-label="Acompanhamento">
        <div className="col-md-8 col-lg-8">
          <Card padding="lg" className="h-full">
            <CardHeader
              title="Como o atendimento flui"
              description="Etapas implementadas no backend atual, do recebimento da mensagem à revisão humana."
            />
            <FlowDiagram />
          </Card>
        </div>
        <div className="col-md-8 col-lg-4">
          <ApiHealthCard />
        </div>
      </section>

      <section className="section grid" aria-label="Atividade recente">
        <div className="col-md-8 col-lg-8">
          <Card padding="lg" className="h-full">
            <CardHeader
              title="Atividade recente"
              action={
                <Link to="/mensagens" className="text-link">
                  Mensagens <Icon name="arrowRight" size={16} />
                </Link>
              }
            />
            <EmptyState
              icon="clock"
              title="Nenhuma atividade para exibir"
              description="A atividade recente aparecerá aqui quando o backend disponibilizar a consulta de mensagens e triagens."
            />
          </Card>
        </div>
        <div className="col-md-8 col-lg-4">
          <Card tone="glow" padding="lg" className="h-full stack">
            <span className="t-label t-accent">Responsabilidade clínica</span>
            <p className="t-card-title">A decisão final é sempre de um profissional de saúde.</p>
            <ClinicalDisclaimer compact />
          </Card>
        </div>
      </section>
    </>
  );
}
