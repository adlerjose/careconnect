# CareConnect PI

Plataforma de acompanhamento pós-atendimento e triagem auxiliar de pacientes por meio do WhatsApp com suporte de Inteligência Artificial.

---

## 1. Visão Geral e Objetivo

O **CareConnect PI** é uma solução voltada para instituições de saúde e equipes médicas com o propósito de manter um canal proativo de comunicação com pacientes após consultas, procedimentos ou altas hospitalares.

### Fluxo Operacional
1. O paciente envia relatos em mensagem de texto ou áudio pelo WhatsApp.
2. O gateway de comunicação (**Evolution API**) recebe a mensagem e aciona os webhooks do backend.
3. O backend processa os dados e submete o conteúdo clínico não estruturado ao módulo de Inteligência Artificial (**Google Gemini**).
4. O módulo de IA extrai dados clínicos relevantes (sintomas reportados, tempo de evolução, medicamentos em uso) e gera uma **classificação auxiliar de prioridade**.
5. As informações estruturadas são validadas e armazenadas em banco de dados **PostgreSQL**.
6. Uma aplicação web responsiva em **React** disponibiliza um painel de controle para que os profissionais de saúde acompanhem os pacientes e priorizem atendimentos.

> **Aviso Ético e Legal**: O sistema CareConnect e seus módulos de IA realizam triagem e suporte operacional auxiliar. A plataforma **NÃO diagnostica doenças, NÃO prescreve medicamentos e NÃO substitui a avaliação de um profissional de saúde qualificado**.

---

## 2. Tecnologias Utilizadas

### Backend
- **Linguagem**: [Python 3.11+](https://www.python.org/)
- **Framework Web**: [FastAPI](https://fastapi.tiangolo.com/) (assíncrono, alta performance e tipagem estática)
- **Validação de Dados e Configuração**: [Pydantic v2](https://docs.pydantic.dev/) e `pydantic-settings`
- **Servidor ASGI**: [Uvicorn](https://www.uvicorn.org/)
- **Testes Automatizados**: [Pytest](https://docs.pytest.org/) e [HTTPX](https://www.python-httpx.org/)

### Frontend
- **Framework**: React 18 com React Router 6
- **Build**: Vite 5
- **Linguagem**: TypeScript strict
- **Estilos**: CSS puro com design tokens centralizados
- **Testes**: Vitest e Testing Library
- **Porta local**: `3000`

### Tecnologias em Fases Futuras
- **Banco de Dados**: PostgreSQL (persistência relacional)
- **Módulo de IA**: Google Gemini API (modelos de linguagem multimodal)
- **Gateway WhatsApp**: Evolution API
- **Containerização**: Docker e Docker Compose

---

## 3. Estrutura de Diretórios

O projeto adota uma arquitetura de **Monólito Modular**, permitindo divisão clara de responsabilidades, alta coesão e independência entre os membros da equipe:

```text
careconnect/
├── backend/
│   ├── .env.example              # Modelo documentado de variáveis de ambiente
│   ├── requirements.txt          # Dependências mínimas essenciais do backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py               # Ponto de entrada FastAPI, middlewares e lifespans
│   │   ├── core/                 # Núcleo compartilhado da aplicação
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Configurações centralizadas via Pydantic Settings
│   │   │   └── logging.py        # Configuração de logs padronizados
│   │   ├── api/                  # Camada de transporte HTTP e roteamento
│   │   │   ├── __init__.py
│   │   │   └── routes/
│   │   │       ├── __init__.py   # Agregador central de rotas versionadas
│   │   │       └── health.py     # Endpoint GET /health e schemas de integridade
│   │   ├── modules/              # Módulos de domínio de negócio isolados
│   │   │   ├── __init__.py
│   │   │   ├── ai/               # Módulo de Inteligência Artificial (Google Gemini)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── pipelines/    # Pipelines de processamento de texto e áudio
│   │   │   │   ├── prompts/      # Engenharia de prompts e templates
│   │   │   │   ├── schemas/      # Schemas de extração e resposta da IA
│   │   │   │   ├── services/     # Clientes de comunicação com a API Gemini
│   │   │   │   └── tests/        # Testes específicos do módulo de IA
│   │   │   ├── messages/         # Recepção e processamento de mensagens do WhatsApp
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas/
│   │   │   │   └── services/
│   │   │   ├── patients/         # Gestão de pacientes e dados cadastrais
│   │   │   │   ├── __init__.py
│   │   │   │   ├── schemas/
│   │   │   │   └── services/
│   │   │   └── triage/           # Regras de triagem e classificação de risco
│   │   │       ├── __init__.py
│   │   │       ├── schemas/
│   │   │       └── services/
│   │   └── shared/               # Utilitários compartilhados transversais
│   │       └── __init__.py
│   └── tests/                    # Suíte de testes automatizados da aplicação
│       ├── __init__.py
│       ├── conftest.py           # Fixtures do Pytest (TestClient HTTP)
│       └── test_health.py        # Testes de disponibilidade e integridade
├── .gitignore                    # Regras de exclusão Git (Python, venv, .env, IDEs)
└── README.md                     # Documentação técnica do projeto
```

---

## 4. Pré-requisitos

- **Python 3.11** ou superior instalado no sistema.
- **Git** configurado.

---

## 5. Como Executar o Backend

### 5.1. Clonar o repositório e acessar a pasta do backend

```bash
git clone https://github.com/<seu-usuario>/careconnect.git
cd careconnect/backend
```

### 5.2. Criar e ativar o ambiente virtual

No Linux / macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

No Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 5.3. Instalar as dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.4. Configurar as variáveis de ambiente

Crie uma cópia do arquivo de exemplo `.env.example`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` caso deseje alterar portas, origens CORS ou chaves para integrações locais.

### 5.5. Executar o servidor de desenvolvimento

Com o ambiente virtual ativado:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Ou diretamente via Python:

```bash
python -m app.main
```

A API estará disponível em: **`http://localhost:8000`**

---

## 6. Documentação Interativa da API

Com a aplicação em execução, acesse a documentação OpenAPI gerada automaticamente:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **OpenAPI JSON**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

### Endpoint de Health Check

- **GET `/health`** ou **GET `/api/v1/health`**
- **Resposta esperada (`200 OK`)**:
  ```json
  {
    "status": "ok",
    "app_name": "CareConnect PI",
    "version": "0.1.0",
    "environment": "development"
  }
  ```

---

## 7. Execução dos Testes Automatizados

Com o ambiente virtual ativo, execute a suíte de testes a partir do diretório `backend`:

```bash
pytest
```

Para visualização detalhada com saída verbosa:

```bash
pytest -v
```

Ou executando a partir da raiz do repositório:

```bash
PYTHONPATH=backend pytest backend/tests -v
```

---

## 8. Stack local e webhook WhatsApp (M1)

Na pasta `backend`, copie `.env.example` para `.env`, ajuste `EVOLUTION_API_KEY` e
inicie a stack:

```bash
docker compose up -d --build
```

O Compose aplica as migrations Alembic antes de iniciar a API. A Evolution API
envia eventos `messages.upsert` para `POST /webhook/whatsapp`; a rota valida o
header `apikey` e agenda a persistência de mensagens recebidas como tarefa em
background. Eventos de conexão, mensagens enviadas pela própria instância,
grupos e status são ignorados. Mensagens de texto e áudio são armazenadas com o
payload bruto; mensagens ainda não processadas ficam com `processed_at` nulo.

Exemplo de teste local (substitua o header pelo valor configurado no `.env`):

```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H 'Content-Type: application/json' \
  -H 'apikey: troque_esta_chave_em_producao' \
  -d '{
    "event": "messages.upsert",
    "instance": "careconnect-dev",
    "data": {
      "key": {
        "remoteJid": "558699999999@s.whatsapp.net",
        "id": "TEST_MSG_123"
      },
      "pushName": "Paciente de teste",
      "message": {"conversation": "Mensagem de teste"}
    }
  }'
```

O endpoint confirma o recebimento antes da persistência em background. O HTTP
200, portanto, não confirma que o commit no banco terminou; `BackgroundTasks`
é adequado ao escopo inicial, mas não substitui uma fila durável para garantias
de processamento em caso de reinício do processo.

---

## 9. Frontend web (branch `develop-front`)

O frontend React foi integrado ao repositório na branch `develop-front`.
Os arquivos da interface ficam isolados no diretório `frontend/`, sem misturar
código da SPA com os módulos Python do backend.

### 9.1. Estrutura do frontend

- React 18, React Router 6 e TypeScript strict.
- Vite 5 para desenvolvimento e build de produção.
- Vitest e Testing Library para testes automatizados.
- Desenvolvimento na porta `3000`.
- Proxy de `/api` e `/health` para o backend em `http://localhost:8000`.

### 9.2. Execução completa

Em terminais separados:

```bash
# Backend
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

A interface estará em `http://localhost:3000` e a API em
`http://localhost:8000`.

### 9.3. Telas disponíveis

| Rota | Tela |
| --- | --- |
| `/` | Dashboard operacional |
| `/pacientes` | Lista de pacientes |
| `/pacientes/ficha` | Ficha do paciente |
| `/mensagens` | Mensagens |
| `/triagem` | Triagem |
| `/sistema` | Estado e documentação do sistema |

As telas de Pacientes, Mensagens e Triagem são protótipos visuais funcionais:
os endpoints de leitura ainda não existem no backend e a interface informa
essa condição em vez de inventar dados.

### 9.4. Validação realizada

- `20` testes Vitest passaram.
- `npm run build` concluiu a geração do bundle de produção.
- Os endpoints `/health` e `/api/v1/health` responderam com `status: "ok"` no
  ambiente local.
- O dashboard, a lista de pacientes, a ficha, mensagens, triagem e sistema
  foram carregados no navegador em uma resolução de desktop.

O build pode emitir avisos para os arquivos comerciais da Neue Montreal,
ausentes no repositório. Nesse caso, a interface usa a fonte Inter
auto-hospedada como substituta.
