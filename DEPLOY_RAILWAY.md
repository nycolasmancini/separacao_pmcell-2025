# 🚂 Deploy PMCELL no Railway

Guia passo a passo para fazer deploy no Railway - **custo estimado: R$ 25-75/mês** para 10 acessos simultâneos.

## 💰 **Por que Railway?**

- ✅ **Barato**: Pay-per-use, sem taxas fixas altas
- ✅ **Simples**: Deploy automático via GitHub
- ✅ **Completo**: Backend + Frontend + PostgreSQL
- ✅ **Brasileiro-friendly**: Aceita cartão brasileiro
- ✅ **Configuração pronta**: Já temos tudo configurado

## 📋 **Pré-requisitos**

1. Conta no GitHub (gratuita)
2. Cartão de crédito (para Railway)
3. Código já comitado no GitHub

## 🔧 **Passo 1: Preparar Repositório**

### 1.1. Inicializar Git (se não feito)
```bash
cd /Users/nycolasmancini/Desktop/pmcell-separacao
git init
git add .
git commit -m "Initial commit - PMCELL ready for deploy"
```

### 1.2. Criar repositório no GitHub
1. Acesse [github.com/new](https://github.com/new)
2. Nome: `pmcell-separacao`
3. Público ou Privado (sua escolha)
4. Clique em "Create repository"

### 1.3. Fazer push para GitHub
```bash
git remote add origin https://github.com/SEU_USERNAME/pmcell-separacao.git
git branch -M main
git push -u origin main
```

## 🚂 **Passo 2: Criar Conta no Railway**

### 2.1. Acessar Railway
1. Vá para [railway.app](https://railway.app)
2. Clique em "Start Building"
3. Faça login com GitHub

### 2.2. Conectar Cartão
1. Vá em Settings > Billing
2. Adicione método de pagamento
3. **Custo estimado**: $5-15/mês (R$ 25-75)

## 🗄️ **Passo 3: Criar Banco PostgreSQL**

### 3.1. Novo Projeto
1. Dashboard Railway > "New Project"
2. Selecione "Deploy from GitHub repo"
3. Escolha seu repositório `pmcell-separacao`

### 3.2. Adicionar PostgreSQL
1. No projeto > "Add Service"
2. Escolha "Database" > "PostgreSQL"
3. Aguarde provisionar (~2 minutos)

### 3.3. Obter URL do Banco
1. Clique no serviço PostgreSQL
2. Aba "Variables"
3. Copie o valor de `DATABASE_URL`

## ⚙️ **Passo 4: Configurar Backend**

### 4.1. Criar Serviço Backend
1. No projeto > "Add Service"
2. Escolha "GitHub Repo"
3. Root Directory: `backend`

### 4.2. Configurar Variáveis de Ambiente
Clique no serviço backend > Variables > Add Variables:

```env
SECRET_KEY=pmcell-super-secure-jwt-key-2025-production
ADMIN_PASSWORD=thmpv321
ENVIRONMENT=production
DEBUG=False
ALLOWED_ORIGINS=https://SEU_FRONTEND_URL.railway.app
DATABASE_URL=postgresql+asyncpg://... (da etapa 3.3)
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### 4.3. Configurar Build
1. Aba "Settings"
2. Build Command: (deixar vazio, usa Dockerfile)
3. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`

## 🎨 **Passo 5: Configurar Frontend**

### 5.1. Criar Serviço Frontend
1. No projeto > "Add Service"
2. Escolha "GitHub Repo" 
3. Root Directory: `frontend`

### 5.2. Configurar Variáveis de Ambiente
```env
VITE_API_URL=https://SEU_BACKEND_URL.railway.app/api/v1
NODE_ENV=production
```

### 5.3. Obter URLs dos Serviços
1. Backend: Aba "Settings" > Public Domain
2. Frontend: Aba "Settings" > Public Domain
3. **Anotar ambas as URLs**

### 5.4. Atualizar CORS
1. Volte ao serviço backend
2. Edite `ALLOWED_ORIGINS` com a URL do frontend
3. Redeploy automático

## 🧪 **Passo 6: Teste da Aplicação**

### 6.1. Aguardar Deploy
- Backend: ~3-5 minutos
- Frontend: ~2-3 minutos
- Status em "Deployments"

### 6.2. Testar Backend
```bash
curl https://SEU_BACKEND_URL.railway.app/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "service": "PMCELL - Separação de Pedidos",
  "version": "1.0.0"
}
```

### 6.3. Testar Frontend
1. Acesse `https://SEU_FRONTEND_URL.railway.app`
2. Deve carregar a tela de login
3. Teste login com PIN: `1234`

## 🔧 **Passo 7: Configuração Final**

### 7.1. Configurar Domínio (Opcional)
1. No serviço frontend > Settings > Public Domain
2. "Add Custom Domain"
3. Digite seu domínio
4. Configure DNS conforme instruções

### 7.2. Configurar Backup
```bash
# Em seu servidor local ou cron job
DATABASE_URL="postgresql://..." ./scripts/backup.sh
```

## 💡 **Comandos Úteis**

### Ver Logs
```bash
# Instalar Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login
railway login

# Ver logs
railway logs --service backend
railway logs --service frontend
```

### Redeploy Manual
```bash
railway up --service backend
railway up --service frontend
```

### Variáveis de Ambiente
```bash
railway variables set SECRET_KEY=nova-chave --service backend
```

## 📊 **Monitoramento de Custos**

### 7.1. Acompanhar Gastos
1. Railway Dashboard > Settings > Billing
2. "Usage" para ver consumo atual
3. "Usage Limits" para definir limites

### 7.2. Otimizar Custos
- **Sleep Mode**: Serviços dormem após inatividade
- **Scaling**: Ajustar recursos conforme necessário
- **Monitoring**: Alertas de uso

## ⚠️ **Estimativa de Custos**

Para **10 acessos simultâneos**:

| Recurso | Uso Estimado | Custo/Mês (USD) |
|---------|--------------|------------------|
| Backend (512MB RAM) | 24/7 | $5-8 |
| Frontend (CDN) | Requests | $1-2 |
| PostgreSQL | Hobby | $5 |
| **Total** | - | **$11-15** |

**Em Reais**: R$ 55-75/mês (câmbio 5.0)

## 🆘 **Troubleshooting**

### Backend não conecta no banco
```bash
# Verificar DATABASE_URL
railway variables --service backend

# Ver logs de erro
railway logs --service backend --tail
```

### Frontend não carrega
1. Verificar VITE_API_URL nas variáveis
2. Testar se backend responde no health check
3. Verificar CORS no backend

### CORS Error
1. Verificar ALLOWED_ORIGINS no backend
2. Deve incluir URL do frontend
3. Formato: `https://frontend-url.railway.app`

## ✅ **Checklist de Deploy**

- [ ] Repositório no GitHub
- [ ] Conta Railway criada
- [ ] PostgreSQL provisionado
- [ ] Backend deployado
- [ ] Frontend deployado
- [ ] Variáveis configuradas
- [ ] URLs funcionando
- [ ] CORS configurado
- [ ] Backup configurado
- [ ] Monitoramento ativo

## 🎉 **Resultado Final**

Após seguir todos os passos, você terá:

- ✅ **Backend**: `https://pmcell-backend-xxx.railway.app`
- ✅ **Frontend**: `https://pmcell-frontend-xxx.railway.app`
- ✅ **Database**: PostgreSQL gerenciado
- ✅ **Custo**: ~R$ 60/mês
- ✅ **Capacidade**: 10+ usuários simultâneos
- ✅ **Backup**: Scripts configurados
- ✅ **Monitoramento**: Health checks

---

**Pronto! Sua aplicação PMCELL está em produção! 🚀**