# CLAUDE.md - PMCELL Separação de Pedidos

Este arquivo contém instruções específicas para o desenvolvimento do sistema PMCELL de separação de pedidos.

## Visão Geral do Projeto

Sistema web para gerenciamento de separação de pedidos, substituindo a solução atual em Bubble.io por uma plataforma própria mais econômica e com maior controle.

## Requisitos Funcionais

### 1. Tela Inicial - Dashboard
- Cards de pedidos em separação mostrando:
  - Nome do cliente
  - Número do orçamento
  - Quantidade de itens (não modelos)
  - Nome do vendedor
  - Valor do pedido
  - % de conclusão
  - Fotos circulares pequenas dos usuários acessando o pedido

### 2. Inserção de Pedidos
- Upload de PDFs (arrastar ou clicar)
- Seleção de logística: Lalamove, Correios, Melhor Envio, Retirada, Entrega, Cliente na loja, Ônibus
- Tipo de embalagem: Caixa ou Sacola
- Campo de observações
- Tela de confirmação mostrando dados extraídos do PDF
- Parser deve ler 100% dos produtos

### 3. Separação de Pedidos
- Login simples com PIN (ex: 1234)
- Cabeçalho com informações do pedido
- Lista de produtos em ordem alfabética
- Cores alternadas nas linhas
- Click para marcar item como separado
- Menu para enviar item para compras ou marcar como não enviado
- Interface otimizada para PC e tablet

### 4. Tela de Compras
- Visualização de todos os itens em compras
- Agrupamento por pedido

### 5. Painel Administrativo
- Senha de acesso: "thmpv321"
- Relatórios de tempo de separação
- Gráfico misto dos últimos 30 dias (linha: tempo, barra: quantidade)
- CRUD de usuários (vendedores, separadores, compradores)
- Métricas por separador

## Requisitos Técnicos

### Stack Tecnológica
- **Backend**: Python 3.11 + FastAPI
- **Frontend**: React 18 + Vite + TailwindCSS
- **Banco**: SQLite (desenvolvimento) → PostgreSQL (produção)
- **PDF**: pdfplumber + PyPDF2
- **Tempo Real**: WebSockets
- **Deploy**: Railway ou Render (~$5-10/mês)

### Padrões de Desenvolvimento

#### TDD Rigoroso
- Cobertura mínima de 90%
- Testes unitários para cada funcionalidade
- Testes de edge cases obrigatórios
- Todos os testes devem passar antes de prosseguir

#### Estrutura de Testes
```python
# Backend (pytest)
tests/
├── unit/          # Testes unitários
├── integration/   # Testes de integração
├── e2e/          # Testes end-to-end
└── fixtures/     # Dados de teste e PDFs

# Frontend (Jest + React Testing Library)
src/
├── components/__tests__/
├── pages/__tests__/
└── services/__tests__/
```

### UI/UX Guidelines

#### Design System
- **Cor Principal**: Laranja (#f97316)
- **Cores de Apoio**: 
  - Laranja escuro (#ea580c)
  - Laranja claro (#fb923c)
  - Cinza para backgrounds (#f9fafb)
  - Texto principal (#111827)

#### Interface
- Design moderno, clean e minimalista
- Responsivo para tablets (min: 768px) e PCs
- Feedback visual imediato (loading states, toasts)
- Animações suaves com Framer Motion
- Teclado numérico touchscreen para login em tablets

#### Logo e Branding
- Nome: "PMCELL - Separação de Pedidos"
- Logo em tons de laranja
- Fonte: Inter ou similar (sans-serif moderna)

## Padrões de Extração de PDF

Baseado na análise dos PDFs fornecidos:

```python
# Patterns para extração
PATTERNS = {
    'order_number': r'Orçamento Nº:\s*(\d+)',
    'client': r'Cliente:\s*([^\n]+?)(?:Forma|$)',
    'seller': r'Vendedor:\s*([^\n]+?)(?:Validade|$)', 
    'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
    'total_value': r'VALOR A PAGAR\s*R\$\s*([\d\.,]+)',
    'items': r'(\d+)\s*/\s*([^-]+)-->\s*([^/]+)/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
}

# Estrutura do item: código / referência --> nome / UN / quantidade / valor_unit / total
```

## Workflow de Desenvolvimento

### Uso do fases.md
1. Consultar fase atual no arquivo `fases.md`
2. Implementar todas as tarefas da fase
3. Executar todos os testes da fase
4. Atualizar status em `fases.md`
5. Usar `/clear` antes de iniciar próxima fase

### Comandos Essenciais
```bash
# Desenvolvimento
make dev        # Inicia frontend e backend
make test       # Executa todos os testes
make lint       # Verifica código

# Testes específicos
make test-backend   # Apenas backend
make test-frontend  # Apenas frontend
make test-e2e       # End-to-end

# Deploy
make build      # Build de produção
make deploy     # Deploy para Railway/Render
```

## Estrutura de Diretórios

```
pmcell-separacao/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints
│   │   ├── core/         # Config, security
│   │   ├── models/       # SQLAlchemy
│   │   ├── schemas/      # Pydantic
│   │   ├── services/     # Business logic
│   │   └── tests/        # Testes
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/   # Componentes React
│   │   ├── pages/        # Páginas
│   │   ├── services/     # API calls
│   │   ├── hooks/        # Custom hooks
│   │   └── utils/        # Helpers
│   └── package.json
├── docker-compose.yml
├── Makefile
├── fases.md
└── CLAUDE.md
```

## Decisões Arquiteturais

### Backend
- **FastAPI** para performance e documentação automática
- **SQLAlchemy** com repository pattern
- **Pydantic** para validação de dados
- **JWT** para autenticação
- **WebSockets** nativos do FastAPI

### Frontend
- **React Query** para cache e estado do servidor
- **Zustand** para estado global
- **React Hook Form** para formulários
- **Recharts** para gráficos
- **Framer Motion** para animações

### Segurança
- Senhas/PINs hasheados com bcrypt
- Tokens JWT com expiração
- CORS configurado corretamente
- Rate limiting nos endpoints
- Validação rigorosa de inputs

## Regras de Negócio

1. **Separação de Pedidos**
   - Apenas um separador por vez pode acessar um pedido
   - Progresso calculado por itens separados / total
   - Itens em compras não contam como separados

2. **Níveis de Acesso**
   - Vendedor: criar pedidos, visualizar próprios pedidos
   - Separador: acessar e separar qualquer pedido
   - Comprador: visualizar itens em compras
   - Admin: acesso total + relatórios

3. **Tempo de Separação**
   - Calculado do primeiro acesso até 100% separado
   - Pausas (sair e voltar) são descontadas
   - Métricas por separador e por período

## Performance

- Lazy loading de componentes
- Paginação server-side (20 itens/página)
- Cache de PDFs processados (15 min)
- Compressão gzip
- CDN para assets estáticos

## Monitoramento

- Logs estruturados (JSON)
- Sentry para erros em produção
- Métricas de performance
- Health checks para uptime
- Backup diário do banco

## Conhecimento Adquirido

_Esta seção será atualizada conforme dúvidas forem respondidas durante o desenvolvimento._

### PDFs
- Estrutura consistente da PMCELL São Paulo
- Campos sempre presentes: número, cliente, vendedor, valor, itens
- Formato do item: código / ref --> nome / UN / qtd / valor_unit / total

### Usuários
- Equipe de até 10 pessoas
- Login simplificado por PIN
- Uso principal em tablets na área de separação

### Integração
- Sistema isolado, sem integração com ERP
- Upload manual de PDFs
- Foco em simplicidade e velocidade