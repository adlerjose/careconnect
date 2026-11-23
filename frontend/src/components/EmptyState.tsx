import type { ReactNode } from 'react';
import { Icon, type IconName } from './Icon';

interface EmptyStateProps {
  icon?: IconName;
  title: string;
  description?: ReactNode;
  children?: ReactNode;
  compact?: boolean;
}

export function EmptyState({ icon = 'info', title, description, children, compact = false }: EmptyStateProps) {
  return (
    <div className={`empty-state${compact ? ' empty-state--compact' : ''}`} role="status">
      <span className="empty-state__icon">
        <Icon name={icon} size={compact ? 20 : 24} />
      </span>
      <div className="stack stack--xs">
        <p className="empty-state__title t-medium">{title}</p>
        {description && <p className="t-small t-muted">{description}</p>}
      </div>
      {children}
    </div>
  );
}
