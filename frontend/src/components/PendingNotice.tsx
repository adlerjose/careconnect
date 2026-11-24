import { PENDING_DEPENDENCIES, type PendingResource } from '../config/pendingDependencies';
import { Icon } from './Icon';

interface PendingNoticeProps {
  resources: PendingResource[];
}

/**
 * Aviso padronizado de integração pendente.
 * Deixa explícito que a tela é estrutura visual e quais endpoints faltam.
 */
export function PendingNotice({ resources }: PendingNoticeProps) {
  const items = resources.map((r) => PENDING_DEPENDENCIES[r]);
  return (
    <aside className="pending-notice" aria-label="Integração pendente">
      <span className="pending-notice__icon">
        <Icon name="plug" size={20} />
      </span>
      <div className="stack stack--sm">
        <p className="t-medium">Integração pendente — esta tela exibe apenas a estrutura visual.</p>
        <p className="t-small t-muted">
          Nenhum dado é exibido porque o backend ainda não oferece os endpoints de leitura abaixo. Nenhuma
          informação fictícia é apresentada.
        </p>
        <ul className="pending-notice__list">
          {items.map((item) => (
            <li key={item.resource}>
              <code className="t-mono">{item.plannedPath}</code>
              <span className="t-small t-muted">{item.description}</span>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
