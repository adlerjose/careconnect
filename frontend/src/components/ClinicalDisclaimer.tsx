import { Icon } from './Icon';

/** Aviso de responsabilidade clínica, reutilizado em telas com conteúdo de IA. */
export function ClinicalDisclaimer({ compact = false }: { compact?: boolean }) {
  return (
    <div className={`clinical-note${compact ? ' clinical-note--compact' : ''}`} role="note">
      <Icon name="shield" size={20} />
      <p className="t-small">
        <strong className="t-medium">A IA auxilia, não diagnostica.</strong> As informações extraídas refletem apenas o
        que o paciente relatou e não substituem a avaliação de um profissional de saúde.
      </p>
    </div>
  );
}
