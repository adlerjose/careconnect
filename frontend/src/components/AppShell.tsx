import { useEffect, useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { useApiHealth } from '../context/HealthContext';
import { formatEnvironment } from '../utils/format';
import { ApiStatusPill } from './ApiStatusPill';
import { Icon, type IconName } from './Icon';

interface NavItem {
  to: string;
  label: string;
  icon: IconName;
  end?: boolean;
}

export const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Visão geral', icon: 'overview', end: true },
  { to: '/pacientes', label: 'Pacientes', icon: 'users' },
  { to: '/mensagens', label: 'Mensagens', icon: 'message' },
  { to: '/triagem', label: 'Triagem', icon: 'pulse' },
  { to: '/sistema', label: 'Sistema', icon: 'server' },
];

function BrandMark() {
  return (
    <svg width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="9" fill="var(--color-ink)" />
      <g stroke="var(--color-sand)" strokeWidth="2.4" strokeLinecap="round">
        <path d="M16 8v16M8 16h16M10.3 10.3l11.4 11.4M21.7 10.3 10.3 21.7" />
      </g>
    </svg>
  );
}

export function AppShell() {
  const [menuOpen, setMenuOpen] = useState(false);
  const location = useLocation();
  const { data } = useApiHealth();

  // Fecha o menu móvel ao navegar
  useEffect(() => setMenuOpen(false), [location.pathname]);

  // Fecha o menu com Esc
  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && setMenuOpen(false);
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [menuOpen]);

  return (
    <div className="app">
      <a className="skip-link" href="#conteudo">
        Pular para o conteúdo
      </a>

      <header className="site-header">
        <div className="container">
          <div className="site-header__bar">
            <NavLink to="/" className="brand" aria-label="CareConnect — Visão geral">
              <BrandMark />
              <span className="brand__name">CareConnect</span>
            </NavLink>

            <nav className="main-nav" aria-label="Navegação principal">
              <ul>
                {NAV_ITEMS.map((item) => (
                  <li key={item.to}>
                    <NavLink to={item.to} end={item.end} className="main-nav__link">
                      {item.label}
                    </NavLink>
                  </li>
                ))}
              </ul>
            </nav>

            <div className="site-header__end">
              <ApiStatusPill />
              <button
                type="button"
                className="icon-button menu-toggle"
                aria-expanded={menuOpen}
                aria-controls="mobile-nav"
                aria-label={menuOpen ? 'Fechar menu' : 'Abrir menu'}
                onClick={() => setMenuOpen((v) => !v)}
              >
                <Icon name={menuOpen ? 'close' : 'menu'} />
              </button>
            </div>
          </div>

          <nav
            id="mobile-nav"
            className={`mobile-nav${menuOpen ? ' is-open' : ''}`}
            aria-label="Navegação principal (móvel)"
            hidden={!menuOpen}
          >
            <ul>
              {NAV_ITEMS.map((item) => (
                <li key={item.to}>
                  <NavLink to={item.to} end={item.end} className="mobile-nav__link">
                    <Icon name={item.icon} />
                    {item.label}
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
        </div>
      </header>

      <main id="conteudo" className="app__main" tabIndex={-1}>
        <div className="container">
          <Outlet />
        </div>
      </main>

      <footer className="site-footer">
        <div className="container site-footer__inner">
          <p className="t-small t-muted">
            A inteligência artificial auxilia a organização e a triagem das informações. Ela não substitui a avaliação
            clínica de um profissional de saúde.
          </p>
          <p className="t-label t-muted">
            {data ? `${data.app_name} · v${data.version} · ${formatEnvironment(data.environment)}` : 'CareConnect'}
          </p>
        </div>
      </footer>
    </div>
  );
}
