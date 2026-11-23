import type { ReactNode } from 'react';
import { Tag } from './Tag';

interface PageHeaderProps {
  eyebrow: string;
  title: string;
  /** Segunda linha do título em Sepia, como em "section by section". */
  accent?: string;
  description?: ReactNode;
  aside?: ReactNode;
}

export function PageHeader({ eyebrow, title, accent, description, aside }: PageHeaderProps) {
  return (
    <header className="page-header grid">
      <div className="page-header__main col-md-8 col-lg-7 stack stack--lg">
        <div>
          <Tag>{eyebrow}</Tag>
        </div>
        <h1 className="t-display">
          {title}
          {accent && (
            <>
              <br />
              <span className="t-accent">{accent}</span>
            </>
          )}
        </h1>
      </div>
      {(description || aside) && (
        <div className="page-header__aside col-md-8 col-lg-5 stack">
          {description && <p className="t-body-lg t-muted page-header__desc">{description}</p>}
          {aside}
        </div>
      )}
    </header>
  );
}
