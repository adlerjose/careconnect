import { useId, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/Card';
import { EmptyState } from '../components/EmptyState';
import { Icon } from '../components/Icon';
import { PageHeader } from '../components/PageHeader';
import { PendingNotice } from '../components/PendingNotice';
import { TableShell, type TableColumn } from '../components/TableShell';
import { Tag } from '../components/Tag';

const COLUMNS: TableColumn[] = [
  { key: 'name', label: 'Paciente' },
  { key: 'whatsapp', label: 'WhatsApp' },
  { key: 'created', label: 'Cadastrado em', hideOnMobile: true },
  { key: 'followup', label: 'Acompanhamento', hideOnMobile: true },
];

export function PatientsPage() {
  const searchId = useId();
  const [query, setQuery] = useState('');

  return (
    <>
      <PageHeader
        eyebrow="Pacientes"
        title="Pacientes"
        accent="em acompanhamento"
        description="Pacientes são registrados automaticamente quando enviam a primeira mensagem pelo WhatsApp. Não há cadastro manual."
      />

      <section className="section stack stack--lg" aria-label="Lista de pacientes">
        <PendingNotice resources={['patients']} />

        <Card padding="lg" className="stack stack--lg">
          <div className="toolbar">
            <div className="search-field">
              <label htmlFor={searchId} className="sr-only">
                Pesquisar pacientes
              </label>
              <Icon name="search" size={18} />
              <input
                id={searchId}
                type="search"
                placeholder="Pesquisar por nome ou número"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled
                aria-describedby={`${searchId}-hint`}
              />
            </div>
            <p id={`${searchId}-hint`} className="t-small t-muted">
              Pesquisa disponível após a integração com a API de pacientes.
            </p>
          </div>

          <TableShell
            caption="Pacientes em acompanhamento"
            columns={COLUMNS}
            empty={
              <EmptyState
                icon="users"
                title="Nenhum paciente para exibir"
                description="A listagem será preenchida com dados reais assim que o endpoint de leitura de pacientes existir."
              />
            }
          />
        </Card>

        <Card tone="linen" className="prototype-link">
          <div className="stack stack--xs">
            <div>
              <Tag tone="prototype" icon="eyeOff">
                Protótipo visual
              </Tag>
            </div>
            <p className="t-medium">Estrutura da ficha do paciente</p>
            <p className="t-small t-muted">Veja como a ficha será organizada. Não contém dados reais.</p>
          </div>
          <Link to="/pacientes/ficha" className="button button--outline">
            Ver estrutura <Icon name="arrowRight" size={16} />
          </Link>
        </Card>
      </section>
    </>
  );
}
