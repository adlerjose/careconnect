# CareConnect — Frontend

Interface web do CareConnect. É uma camada visual **isolada**: não altera o backend nem depende de código Python.

| Item        | Escolha                                                        |
| ----------- | -------------------------------------------------------------- |
| Stack       | React 18 + Vite 5 + TypeScript (strict)                        |
| Estilos     | CSS puro com design tokens centralizados (`src/styles/tokens.css`) |
| Rotas       | React Router 6                                                 |
| Testes      | Vitest + Testing Library                                       |
| Porta       | `3000` (já liberada em `BACKEND_CORS_ORIGINS` do backend)      |

## Como rodar

```bash
# 1. Backend (em outro terminal) — ver README da raiz
cd backend && uvicorn app.main:app --reload --port 8000

# 2. Frontend
cd frontend
cp .env.example .env   # opcional
npm install
npm run dev            # http://localhost:3000
```

Em desenvolvimento, as requisições para `/health` e `/api/*` são encaminhadas pelo proxy do Vite
para `VITE_PROXY_TARGET` (padrão `http://localhost:8000`). Para apontar direto para outra URL,
defina `VITE_API_BASE_URL` (a origem do frontend precisa estar no CORS do backend).

| Script              | Descrição                         |
| ------------------- | --------------------------------- |
| `npm run dev`       | Servidor de desenvolvimento       |
| `npm run build`     | Verificação de tipos + build      |
| `npm run preview`   | Servir o build na porta 3000      |
| `npm test`          | Testes automatizados              |

## Estrutura

```
frontend/
├── public/
│   ├── favicon.svg
│   └── fonts/README.md        # onde colocar os arquivos licenciados da Neue Montreal
└── src/
    ├── components/            # AppShell, Card, Tag, StatCard, EmptyState, PendingNotice,
    │                          # TableShell, FlowDiagram, ApiStatusPill, ClinicalDisclaimer, Icon
    ├── config/                # env.ts, pendingDependencies.ts (endpoints ainda inexistentes)
    ├── context/               # HealthContext (estado compartilhado de /api/v1/health)
    ├── hooks/                 # useHealth
    ├── pages/                 # Dashboard, Patients, PatientDetail, Messages, Triage, System, NotFound
    ├── services/              # http.ts (fetch com timeout/erros), health.ts
    ├── styles/                # tokens.css, fonts.css, global.css, components.css
    ├── types/                 # domain.ts (espelho dos modelos do backend, sem raw_payload)
    └── utils/                 # format.ts
```

## Integração com o backend

| Endpoint                 | Uso no frontend                                         |
| ------------------------ | ------------------------------------------------------- |
| `GET /api/v1/health`     | **Conectado** — status no cabeçalho, painel e rodapé (a cada 30 s) |
| `GET /health`            | **Conectado** — tela Sistema                             |
| `/docs`                  | Link na tela Sistema                                    |
| `POST /webhook/whatsapp` | **Não utilizado** — é de uso exclusivo da Evolution API  |

### Pendências técnicas

Pacientes, Mensagens, Triagem e Ficha do paciente exibem **apenas estrutura visual**, com aviso
explícito, porque não há endpoints de leitura no backend. Os caminhos previstos (comentados em
`backend/app/api/routes/__init__.py`) estão registrados em `src/config/pendingDependencies.ts`:

- `GET /api/v1/patients`
- `GET /api/v1/patients/{id}`
- `GET /api/v1/messages`
- `GET /api/v1/triage`

Nenhum dado fictício, indicador inventado ou autenticação simulada é apresentado.

## Identidade visual

- **Paleta:** Ink `#0A0A0A`, White `#FFFFFF`, Linen `#F8F4EF`, Sepia `#A0724F`, Sand `#E9C4A6`,
  Stone `#5E5E5E`, Clay `#C98A5E`; gradiente Sepia Glow `#F8F4EF → #E9C4A6`.
- **Tipografia:** Display 56 · Heading 40 · Card 24 · Body 16–18 · Label 12 px; pesos 300/400/500;
  tracking −3% em títulos.
- **Grid:** 12 colunas, gutter 24 px, margem 64 px, frame máximo 1440 px → 8 colunas / margem 32 px
  em tablet → 4 colunas / margem 20 px em smartphone.

### Fonte

**Neue Montreal** é comercial e **não** está no repositório. A pilha tipográfica tenta usá-la
(instalada localmente ou em `public/fonts/`) e, na ausência, usa **Inter** (SIL OFL,
auto-hospedada) como **substituta** — que não é a Neue Montreal. Veja `public/fonts/README.md`.

## Acessibilidade

Link “Pular para o conteúdo”, foco visível, navegação por teclado (menu móvel fecha com Esc),
estados sempre com ícone + texto, `aria-current` na página ativa, `aria-live` no status da API e
respeito a `prefers-reduced-motion`.

## Integração da branch `develop-front`

A branch `develop-front` contém esta aplicação React dentro do monorepositório,
na pasta `frontend/`. A inclusão foi registrada no commit local
`feat: add frontend to develop-front` após a criação da branch.

## Verificação de interface

Em 23 de novembro de 2026, o sistema foi executado localmente em:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`

As seguintes telas foram verificadas no navegador com viewport desktop de
1440 × 900:

| Tela | Rota |
| --- | --- |
| Dashboard | `/` |
| Pacientes | `/pacientes` |
| Ficha do paciente | `/pacientes/ficha` |
| Mensagens | `/mensagens` |
| Triagem | `/triagem` |
| Sistema | `/sistema` |

Validações concluídas:

- 20 testes Vitest passaram.
- `npm run build` foi concluído.
- A API respondeu em `/health` e `/api/v1/health`.
- Todas as rotas da interface carregaram sem falha estrutural.
