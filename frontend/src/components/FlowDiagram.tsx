import { Icon, type IconName } from './Icon';

interface FlowStep {
  icon: IconName;
  title: string;
  detail: string;
  highlight?: boolean;
}

/**
 * Fluxo real implementado no backend (webhook_service.py → extraction_pipeline.py).
 * Descreve a arquitetura existente — não representa dados nem volumes.
 */
const STEPS: FlowStep[] = [
  { icon: 'message', title: 'WhatsApp', detail: 'Paciente envia mensagem via Evolution API' },
  { icon: 'plug', title: 'Webhook', detail: 'POST /webhook/whatsapp valida a chave e aceita o evento' },
  { icon: 'users', title: 'Registro', detail: 'Paciente e mensagem são salvos de forma idempotente' },
  { icon: 'sparkle', title: 'Extração por IA', detail: 'Google Gemini organiza o relato textual' },
  { icon: 'doc', title: 'Triagem', detail: 'Resumo, sintomas relatados e confiança são gravados' },
  { icon: 'shield', title: 'Revisão humana', detail: 'Profissional de saúde avalia os casos sinalizados', highlight: true },
];

export function FlowDiagram() {
  return (
    <ol className="flow" aria-label="Fluxo de processamento das mensagens">
      {STEPS.map((step, i) => (
        <li key={step.title} className={`flow__step${step.highlight ? ' flow__step--highlight' : ''}`}>
          <span className="flow__node">
            <Icon name={step.icon} size={18} />
          </span>
          <div className="flow__text">
            <span className="t-label t-muted">{String(i + 1).padStart(2, '0')}</span>
            <p className="t-medium">{step.title}</p>
            <p className="t-small t-muted">{step.detail}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
