import type { ReactNode } from 'react';

export interface TableColumn {
  key: string;
  label: string;
  /** Oculta a coluna em telas pequenas. */
  hideOnMobile?: boolean;
}

interface TableShellProps {
  caption: string;
  columns: TableColumn[];
  /** Conteúdo exibido quando não há linhas (estado vazio/pendente). */
  empty: ReactNode;
  children?: ReactNode;
}

/** Estrutura de tabela semântica com estado vazio integrado. */
export function TableShell({ caption, columns, empty, children }: TableShellProps) {
  const hasRows = Boolean(children);
  return (
    <div className="table-shell">
      <table>
        <caption className="sr-only">{caption}</caption>
        <thead>
          <tr>
            {columns.map((c) => (
              <th key={c.key} scope="col" className={c.hideOnMobile ? 'hide-mobile' : undefined}>
                {c.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {hasRows ? (
            children
          ) : (
            <tr>
              <td colSpan={columns.length} className="table-shell__empty">
                {empty}
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
