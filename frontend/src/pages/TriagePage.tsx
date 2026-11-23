import { Card, CardHeader } from '../components/Card';
import { ClinicalDisclaimer } from '../components/ClinicalDisclaimer';
import { EmptyState } from '../components/EmptyState';
import { Icon, type IconName } from '../components/Icon';
import { PageHeader } from '../components/PageHeader';
import { PendingNotice } from '../components/PendingNotice';
import { Tag } from '../components/Tag';

/**
 * Campos de ClinicalExtractionResult (backend/app/modules/ai/schemas/clinical.py)
 * e de TriageRecord. Apresentados como anatomia do registro, sem valores.
 */
const RECORD_FIELDS: { icon: IconName; label: string; description: string }[] = [
  { icon: 'doc', label: 'Resumo clínico', description: 'Resumo objetivo do relato, preservando a fala do paciente.' },
  { icon: 'pulse', label: 'Sintomas relatados', description: 'Somente sintomas expressamente mencionados, sem inferências.' },
  { icon: 'clock', label: 'Duração informada', description: 'Tempo de evolução conforme dito pelo paciente.' },
  { icon: 'sparkle', label: 'Medicamentos mencionados', description: 'Medicamentos que o paciente informou usar ou ter usado.' },
  { icon: 'info', label: 'Nível de confiança', description: 'Grau de aderência estimado pelo modelo, de 0 a 100%.' },
  { icon: 'message', label: 'Mensagem relacionada', description: 'Mensagem do WhatsApp que originou o registro.' },
];

export function TriagePage() {
  return (
    <>
      <PageHeader
        eyebrow="Triagem"
        title="Triagem auxiliar"
        accent="organizada por IA"
        description="A IA organiza o que o paciente relatou. Ela não emite diagnósticos e sinaliza quando um profissional de saúde precisa revisar o caso."
        aside={<ClinicalDisclaimer />}
      />

      <section className="section stack stack--lg" aria-label="Registros de triagem">
        <PendingNotice resources={['triage']} />

        <Card padding="lg">
          <CardHeader title="Registros" description="Triagens geradas a partir das mensagens de texto recebidas." />
          <EmptyState
            icon="pulse"
            title="Nenhum registro de triagem para exibir"
            description="Os registros são gravados no banco pelo backend, mas ainda não há endpoint de leitura."
          />
        </Card>
      </section>

      <section className="section" aria-labelledby="anatomia">
        <div className="section-intro">
          <div className="cluster">
            <Tag tone="prototype" icon="eyeOff">
              Protótipo visual
            </Tag>
          </div>
          <h2 id="anatomia" className="t-heading">
            Anatomia de um registro
          </h2>
          <p className="t-muted">Como cada triagem será apresentada. Os campos abaixo não contêm dados.</p>
        </div>

        <div className="grid triage-anatomy">
          <div className="col-md-8 col-lg-8">
            <Card padding="lg" className="h-full">
              <ul className="anatomy-list">
                {RECORD_FIELDS.map((f) => (
                  <li key={f.label}>
                    <span className="legend__icon">
                      <Icon name={f.icon} size={18} />
                    </span>
                    <div>
                      <p className="t-medium">{f.label}</p>
                      <p className="t-small t-muted">{f.description}</p>
                    </div>
                    <span className="anatomy-list__value t-small">Sem dados</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>
          <div className="col-md-8 col-lg-4">
            <Card tone="ink" padding="lg" className="h-full review-card">
              <span className="review-card__icon">
                <Icon name="shield" size={22} />
              </span>
              <p className="t-label review-card__eyebrow">Revisão humana</p>
              <p className="t-card-title">Indicador sempre visível</p>
              <p className="t-small review-card__text">
                Quando a IA identifica ambiguidade ou baixa clareza, o registro é marcado como
                <strong> “Requer revisão humana”</strong>. Esse indicador é exibido com destaque, texto e ícone em cada
                triagem.
              </p>
              <EmptyState compact icon="shield" title="Nenhum caso sinalizado para exibir" />
            </Card>
          </div>
        </div>
      </section>
    </>
  );
}
