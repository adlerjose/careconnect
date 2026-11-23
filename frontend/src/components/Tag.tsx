import type { ReactNode } from 'react';
import { Icon, type IconName } from './Icon';

type TagTone = 'ink' | 'sand' | 'outline' | 'prototype';

interface TagProps {
  children: ReactNode;
  tone?: TagTone;
  icon?: IconName;
}

/** Rótulo em pílula (ex.: "PAINEL", "PROTÓTIPO VISUAL"), como nas referências. */
export function Tag({ children, tone = 'ink', icon }: TagProps) {
  return (
    <span className={`tag tag--${tone}`}>
      {icon && <Icon name={icon} size={14} />}
      {children}
    </span>
  );
}

export type StatusTone = 'success' | 'warning' | 'danger' | 'neutral';

const STATUS_ICON: Record<StatusTone, IconName> = {
  success: 'check',
  warning: 'alert',
  danger: 'x',
  neutral: 'clock',
};

interface StatusBadgeProps {
  tone: StatusTone;
  children: ReactNode;
}

/** Estado sempre comunicado por ícone + texto, nunca apenas por cor. */
export function StatusBadge({ tone, children }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge--${tone}`}>
      <Icon name={STATUS_ICON[tone]} size={14} />
      {children}
    </span>
  );
}
