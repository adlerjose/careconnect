import { Link, useParams } from 'react-router-dom';
import { Card, CardHeader } from '../components/Card';
import { ClinicalDisclaimer } from '../components/ClinicalDisclaimer';
import { EmptyState } from '../components/EmptyState';
import { Icon } from '../components/Icon';
import { PendingNotice } from '../components/PendingNotice';
import { Tag } from '../components/Tag';

const IDENTITY_FIELDS = [
  { label: 'Nome', hint: 'Nome de exibição informado no WhatsApp' },
  { label: 'WhatsApp', hint: 'Número exibido de forma mascarada' },
  { label: 'Cadastrado em', hint: 'Data da primeira mensagem recebida' },
];

/**
 * Ficha do paciente.
 * - /pacientes/ficha       => pré-visualização da estrutura (protótipo visual)
 * - /pacientes/:patientId  => mesma estrutura; dados indisponíveis até existir o endpoint
 */
export function PatientDetailPage() {
  const { patientId } = useParams();
  const isPreview = !patientId;

  return (
    <>
      <div className="detail-header">
        <Link to="/pacientes" className="text-link">
          <Icon name="arrowLeft" size={16} /> Pacientes
        </Link>
        <div className="detail-header__title">
          <span className="avatar" aria-hidden="true">
            <Icon name="user" size={28} />
          </span>
          <div className="stack stack--sm">
            <div className="cluster">
              <Tag>Ficha do paciente</Tag>
              {isPreview && (
                <Tag tone="prototype" icon="eyeOff">
                  Protótipo visual
                </Tag>
              )}
            </div>
            <h1 className="t-heading">{isPreview ? 'Estrutura da ficha' : 'Paciente'}</h1>
            {!isPreview && (
              <p className="t-small t-muted">
                Identificador solicitado: <code className="t-mono">{patientId}</code>
              </p>
            )}
          </div>
        </div>
      </div>

      <section className="section stack stack--lg">
        <PendingNotice resources={['patientDetail']} />

        <div className="grid">
          <div className="col-md-8 col-lg-4">
            <Card padding="lg" className="h-full">
              <CardHeader title="Identificação" titleAs="h2" />
              <dl className="field-list">
                {IDENTITY_FIELDS.map((f) => (
                  <div key={f.label} className="field-list__row">
                    <dt className="t-label t-muted">{f.label}</dt>
                    <dd>
                      <span className="field-list__empty">Indisponível</span>
                      <span className="t-small t-muted">{f.hint}</span>
                    </dd>
                  </div>
                ))}
              </dl>
            </Card>
          </div>

          <div className="col-md-8 col-lg-8 stack stack--lg">
            <Card padding="lg">
              <CardHeader title="Histórico de mensagens" description="Mensagens recebidas deste paciente pelo WhatsApp." />
              <EmptyState
                compact
                icon="message"
                title="Histórico indisponível"
                description="Depende de um endpoint de consulta de mensagens por paciente."
              />
            </Card>
            <Card padding="lg">
              <CardHeader title="Registros de triagem" description="Informações organizadas pela IA a partir dos relatos." />
              <EmptyState
                compact
                icon="pulse"
                title="Registros indisponíveis"
                description="Depende de um endpoint de leitura de triagens por paciente."
              />
              <ClinicalDisclaimer compact />
            </Card>
          </div>
        </div>
      </section>
    </>
  );
}
