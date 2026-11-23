import type { ElementType, HTMLAttributes, ReactNode } from 'react';

type CardTone = 'white' | 'ink' | 'linen' | 'glow';

interface CardProps extends HTMLAttributes<HTMLElement> {
  as?: ElementType;
  tone?: CardTone;
  padding?: 'md' | 'lg';
  children: ReactNode;
}

export function Card({ as: Component = 'div', tone = 'white', padding = 'md', className = '', children, ...rest }: CardProps) {
  return (
    <Component className={`card card--${tone} card--pad-${padding} ${className}`.trim()} {...rest}>
      {children}
    </Component>
  );
}

interface CardHeaderProps {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  titleAs?: 'h2' | 'h3';
}

export function CardHeader({ title, description, action, titleAs: Title = 'h2' }: CardHeaderProps) {
  return (
    <div className="card-header">
      <div className="stack stack--xs">
        <Title className="t-card-title">{title}</Title>
        {description && <p className="t-small t-muted">{description}</p>}
      </div>
      {action && <div className="card-header__action">{action}</div>}
    </div>
  );
}
