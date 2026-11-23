import { render, screen, waitFor, within } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { App } from './App';
import { getProcessingState } from './types/domain';
import { maskPhone } from './utils/format';

const OK = { status: 'ok', app_name: 'CareConnect PI', version: '0.1.0', environment: 'development' };

function renderAt(path: string, fetchImpl?: () => Promise<Response>) {
  const fetchMock = vi.fn<(input: RequestInfo | URL, init?: RequestInit) => Promise<Response>>(
    fetchImpl ?? (async () => new Response(JSON.stringify(OK), { status: 200 })),
  );
  vi.stubGlobal('fetch', fetchMock);
  render(
    <MemoryRouter initialEntries={[path]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <App />
    </MemoryRouter>,
  );
  return fetchMock;
}

/** Garante que o frontend só chama endpoints existentes no backend. */
function expectOnlyHealthCalls(fetchMock: { mock: { calls: unknown[][] } }) {
  const urls = fetchMock.mock.calls.map((c) => String(c[0]));
  expect(urls.length).toBeGreaterThan(0);
  for (const url of urls) expect(['/health', '/api/v1/health']).toContain(url);
}

describe('Visão geral', () => {
  it('exibe estado real da API quando online', async () => {
    const fetchMock = renderAt('/');
    expect(await screen.findAllByText('API online')).not.toHaveLength(0);
    expect(screen.getByText(/CareConnect PI · v0\.1\.0 · Desenvolvimento/)).toBeInTheDocument();
    expectOnlyHealthCalls(fetchMock);
  });

  it('exibe estado de indisponibilidade quando a API falha', async () => {
    renderAt('/', async () => {
      throw new TypeError('Failed to fetch');
    });
    expect(await screen.findAllByText('API indisponível')).not.toHaveLength(0);
    expect(screen.getByText(/Não foi possível conectar à API/)).toBeInTheDocument();
  });

  it('não apresenta indicadores numéricos inventados', async () => {
    renderAt('/');
    const region = screen.getByRole('heading', { name: 'Indicadores' }).closest('section')!;
    const values = region.querySelectorAll('.stat-card__value');
    expect(values).toHaveLength(4);
    values.forEach((v) => expect(v.textContent).toBe('—'));
    await waitFor(() => expect(screen.getAllByText('API online').length).toBeGreaterThan(0));
  });
});

describe.each([
  ['/pacientes', 'GET /api/v1/patients'],
  ['/mensagens', 'GET /api/v1/messages'],
  ['/triagem', 'GET /api/v1/triage'],
  ['/pacientes/ficha', 'GET /api/v1/patients/{id}'],
])('Tela %s', (path, pending) => {
  it('sinaliza integração pendente e não chama endpoints inexistentes', async () => {
    const fetchMock = renderAt(path);
    const notice = screen.getByRole('complementary', { name: 'Integração pendente' });
    expect(within(notice).getByText(pending)).toBeInTheDocument();
    await waitFor(() => expect(fetchMock).toHaveBeenCalled());
    expectOnlyHealthCalls(fetchMock);
  });
});

describe('Triagem', () => {
  it('mantém aviso de responsabilidade clínica e revisão humana', () => {
    renderAt('/triagem');
    expect(screen.getByText('A IA auxilia, não diagnostica.')).toBeInTheDocument();
    expect(screen.getByText('Indicador sempre visível')).toBeInTheDocument();
  });
});

describe('Mensagens', () => {
  it('não anuncia transcrição de áudio', () => {
    renderAt('/mensagens');
    expect(screen.getByText(/não há transcrição nem interpretação de áudio/)).toBeInTheDocument();
  });
});

describe('Sistema', () => {
  it('verifica os dois endpoints de saúde', async () => {
    const fetchMock = renderAt('/sistema');
    await waitFor(() => {
      const urls = fetchMock.mock.calls.map((c) => String(c[0]));
      expect(urls).toContain('/health');
      expect(urls).toContain('/api/v1/health');
    });
  });
});

describe('Navegação', () => {
  it('destaca a página ativa', () => {
    renderAt('/mensagens');
    const nav = screen.getByRole('navigation', { name: 'Navegação principal' });
    expect(within(nav).getByRole('link', { name: 'Mensagens' })).toHaveAttribute('aria-current', 'page');
  });

  it('exibe página 404 para rotas desconhecidas', () => {
    renderAt('/rota-inexistente');
    expect(screen.getByText('Página não encontrada')).toBeInTheDocument();
  });
});

describe('Utilitários', () => {
  it('deriva o estado de processamento a partir dos campos reais', () => {
    expect(getProcessingState({ processed_at: null, processing_error: null })).toBe('pending');
    expect(getProcessingState({ processed_at: '2026-01-01', processing_error: null })).toBe('processed');
    expect(getProcessingState({ processed_at: null, processing_error: 'AudioMediaUnavailable' })).toBe('error');
  });

  it('mascara números de WhatsApp', () => {
    expect(maskPhone('5511999998888')).toBe('•••••••••8888');
  });
});
