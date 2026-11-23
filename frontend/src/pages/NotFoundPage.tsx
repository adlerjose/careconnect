import { Link } from 'react-router-dom';
import { EmptyState } from '../components/EmptyState';
import { Icon } from '../components/Icon';

export function NotFoundPage() {
  return (
    <div className="section">
      <EmptyState icon="alert" title="Página não encontrada" description="O endereço acessado não existe nesta interface.">
        <Link to="/" className="button button--ink">
          <Icon name="arrowLeft" size={16} /> Voltar à visão geral
        </Link>
      </EmptyState>
    </div>
  );
}
