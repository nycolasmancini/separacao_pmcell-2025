# PMCELL - Sistema de Separação de Pedidos

Sistema web para gerenciamento de separação de pedidos da PMCELL.

## Stack Tecnológica

- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite + TailwindCSS
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Deploy**: Docker + Docker Compose

## Início Rápido

### Pré-requisitos
- Python 3.11+
- Node.js 20+
- Docker e Docker Compose (opcional)

### Setup Inicial
```bash
make setup
```

### Desenvolvimento
```bash
make dev
```

Acesse:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Docker
```bash
make docker-up
```

### Testes
```bash
make test
```

## Estrutura do Projeto

```
pmcell-separacao/
├── backend/         # API FastAPI
├── frontend/        # App React
├── docker-compose.yml
├── Makefile
└── fases.md        # Roadmap de desenvolvimento
```

## Comandos Úteis

- `make help` - Lista todos os comandos disponíveis
- `make test` - Executa todos os testes
- `make lint` - Verifica código
- `make clean` - Limpa arquivos temporários

## Documentação

- [CLAUDE.md](./CLAUDE.md) - Instruções para desenvolvimento
- [fases.md](./fases.md) - Fases de implementação