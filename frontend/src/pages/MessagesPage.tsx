import { Card, CardHeader } from '../components/Card';
import { EmptyState } from '../components/EmptyState';
import { Icon, type IconName } from '../components/Icon';
import { PageHeader } from '../components/PageHeader';
import { PendingNotice } from '../components/PendingNotice';
import { TableShell, type TableColumn } from '../components/TableShell';
import { StatusBadge, type StatusTone } from '../components/Tag';

const COLUMNS: TableColumn[] = [
  { key: 'patient', label: 'Paciente' },
  { key: 'type', label: 'Tipo' },
  { key: 'content', label: 'Conteúdo', hideOnMobile: true },
  { key: 'received', label: 'Recebida em', hideOnMobile: true },
  { key: 'state', label: 'Processamento' },
];

/** Tipos efetivamente reconhecidos por _extract_message no backend. */
const MESSAGE_TYPES: { icon: IconName; label: string; detail: string }[] = [
  { icon: 'text', label: 'Texto', detail: 'Encaminhada para extração de informações pela IA.' },
  {
    icon: 'mic',
    label: 'Áudio',
    detail: 'Registrada, porém ainda não processada: não há transcrição nem interpretação de áudio no fluxo atual.',
  },
  { icon: 'info', label: 'Outro', detail: 'Formatos não reconhecidos são registrados sem processamento.' },
];

/** Estados derivados de processed_at / processing_error. */
const PROCESSING_STATES: { tone: StatusTone; label: string; detail: string }[] = [
  { tone: 'success', label: 'Processada', detail: 'A triagem foi gerada e registrada.' },
  { tone: 'neutral', label: 'Aguardando', detail: 'Recebida e ainda sem resultado de processamento.' },
  { tone: 'danger', label: 'Erro', detail: 'O processamento falhou e precisa de verificação.' },
];

export function MessagesPage() {
  return (
    <>
      <PageHeader
        eyebrow="Mensagens"
        title="Mensagens"
        accent="recebidas pelo WhatsApp"
        description="Relatos enviados pelos pacientes e o estado do processamento de cada um. Payloads técnicos e dados internos não são exibidos."
      />

      <section className="section stack stack--lg" aria-label="Mensagens">
        <PendingNotice resources={['messages']} />

        <Card padding="lg">
          <TableShell
            caption="Mensagens recebidas"
            columns={COLUMNS}
            empty={
              <EmptyState
                icon="message"
                title="Nenhuma mensagem para exibir"
                description="O endpoint POST /webhook/whatsapp apenas recebe eventos da Evolution API; ele não oferece consulta de mensagens."
              />
            }
          />
        </Card>
      </section>

      <section className="section grid" aria-label="Legenda">
        <div className="col-md-8 col-lg-6">
          <Card padding="lg" className="h-full">
            <CardHeader title="Tipos de mensagem" titleAs="h2" />
            <ul className="legend">
              {MESSAGE_TYPES.map((t) => (
                <li key={t.label}>
                  <span className="legend__icon">
                    <Icon name={t.icon} size={18} />
                  </span>
                  <div>
                    <p className="t-medium">{t.label}</p>
                    <p className="t-small t-muted">{t.detail}</p>
                  </div>
                </li>
              ))}
            </ul>
          </Card>
        </div>
        <div className="col-md-8 col-lg-6">
          <Card padding="lg" className="h-full">
            <CardHeader title="Estados de processamento" titleAs="h2" />
            <ul className="legend">
              {PROCESSING_STATES.map((s) => (
                <li key={s.label}>
                  <StatusBadge tone={s.tone}>{s.label}</StatusBadge>
                  <p className="t-small t-muted">{s.detail}</p>
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </section>
    </>
  );
}
