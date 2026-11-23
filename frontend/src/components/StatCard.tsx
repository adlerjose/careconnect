import { Icon, type IconName } from './Icon';

interface StatCardProps {
  label: string;
  icon: IconName;
  /** Valor real vindo da API. `null` => sem fonte de dados. */
  value: string | number | null;
  unavailableReason?: string;
}

/** Card de indicador. Nunca exibe número sem fonte de dados real. */
export function StatCard({ label, icon, value, unavailableReason = 'Sem fonte de dados na API' }: StatCardProps) {
  const hasValue = value !== null;
  return (
    <article className="stat-card card card--white card--pad-md">
      <div className="stat-card__top">
        <span className="t-small t-muted">{label}</span>
        <span className="stat-card__icon">
          <Icon name={icon} size={18} />
        </span>
      </div>
      <p className={`stat-card__value t-heading${hasValue ? '' : ' stat-card__value--empty'}`}>
        {hasValue ? value : <span aria-label="Indisponível">—</span>}
      </p>
      {!hasValue && (
        <p className="stat-card__caption t-label t-muted">
          <Icon name="plug" size={12} /> {unavailableReason}
        </p>
      )}
    </article>
  );
}
