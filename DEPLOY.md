# Deploy PMCELL - Sistema de Separação

## URLs de Produção

### Frontend (GitHub Pages)
- **URL**: https://nycolasmancini.github.io/separacao_pmcell-2025
- **Status**: ✅ Deployed
- **Hospedagem**: GitHub Pages (gratuito)

### Backend (Render)
- **URL**: https://pmcell-backend.onrender.com
- **API Docs**: https://pmcell-backend.onrender.com/docs
- **Status**: ⏳ Aguardando deploy no Render
- **Hospedagem**: Render.com (free tier)

## Como Fazer Deploy

### Frontend (GitHub Pages)
```bash
cd frontend
npm run deploy
```

### Backend (Render)
1. Acesse https://render.com
2. Crie uma conta gratuita
3. Conecte seu repositório GitHub
4. Selecione o diretório `backend`
5. O Render usará automaticamente o `render.yaml`

## Configurações Importantes

### Variáveis de Ambiente (Backend)
O `render.yaml` já configura automaticamente:
- `DATABASE_URL` - PostgreSQL gratuito do Render
- `SECRET_KEY` - Gerado automaticamente
- `JWT_SECRET_KEY` - Gerado automaticamente
- `ALLOWED_ORIGINS` - https://nycolasmancini.github.io
- `ENVIRONMENT` - production
- `SKIP_SECURITY_VALIDATION` - true

### Limitações do Plano Gratuito

#### Render (Backend)
- Apps "dormem" após 15 minutos de inatividade
- Primeiro acesso após dormir demora ~30 segundos
- PostgreSQL gratuito por 90 dias (precisa recriar)
- 750 horas de execução por mês

#### GitHub Pages (Frontend)
- 100GB de banda por mês
- Apenas arquivos estáticos (perfeito para React)
- Sem limitações de visitantes

## Manutenção

### Atualizar Frontend
```bash
cd frontend
npm run deploy
```

### Atualizar Backend
```bash
git push origin main
# Render faz deploy automático
```

## Acesso para Equipe

Compartilhe com sua equipe de 10 colaboradores:
- **Sistema**: https://nycolasmancini.github.io/separacao_pmcell-2025
- **PIN padrão**: Configure no primeiro acesso
- **Admin**: Senha "thmpv321"

## Troubleshooting

### Frontend não carrega
- Verifique se o GitHub Pages está habilitado nas configurações do repositório
- Branch deve ser `gh-pages`

### Backend não responde
- Pode estar "dormindo" - aguarde 30 segundos
- Verifique logs no dashboard do Render

### Erro de CORS
- Certifique-se que `ALLOWED_ORIGINS` inclui a URL do GitHub Pages
- Backend deve estar rodando em HTTPS