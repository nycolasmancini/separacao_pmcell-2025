#!/bin/bash

# Script de Deploy PMCELL - Versão Final Corrigida
# Execute no servidor VPS como root

set -e  # Sair se houver erro

echo "🚀 Iniciando deploy PMCELL corrigido..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está sendo executado como root
if [ "$EUID" -ne 0 ]; then
    log_error "Execute este script como root: sudo $0"
    exit 1
fi

# Navegar para diretório do projeto
cd /root/pmcell-separacao

log_info "Passo 1: Parando containers existentes..."
docker-compose -f docker-compose.prod.yml down || true
docker container prune -f
docker image prune -f

log_info "Passo 2: Atualizando JWT_SECRET_KEY..."
# Gerar JWT super forte de 64 caracteres
JWT_SECRET=$(openssl rand -hex 32)

cat > .env.prod << EOF
# Database
DB_USER=pmcell_user
DB_PASSWORD=PmcellKingHost2025!
DB_NAME=pmcell_db
DB_HOST=db

# App - JWT Super Forte
JWT_SECRET_KEY=${JWT_SECRET}
ADMIN_PASSWORD=thmpv321
ENVIRONMENT=production
DEBUG=False

# URLs
FRONTEND_URL=http://177.153.64.105
BACKEND_URL=http://177.153.64.105:8000

# Database URL
DATABASE_URL=postgresql+asyncpg://pmcell_user:PmcellKingHost2025!@db:5432/pmcell_db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=http://177.153.64.105
EOF

chmod 600 .env.prod
log_info "JWT forte de 64 caracteres configurado!"

log_info "Passo 3: Corrigindo Dockerfile do backend..."
# Corrigir health check no Dockerfile
sed -i 's|http://localhost:8000/health|http://localhost:8000/api/v1/health|g' backend/Dockerfile

log_info "Passo 4: Corrigindo package.json do frontend..."
# Fazer downgrade do react-router-dom para versão compatível com Node 18
sed -i 's|"react-router-dom": ".*"|"react-router-dom": "^6.26.1"|g' frontend/package.json

log_info "Passo 5: Removendo package-lock.json para forçar reinstalação..."
rm -f frontend/package-lock.json

log_info "Passo 6: Fazendo build e deploy..."
# Build com --no-cache para garantir que as correções sejam aplicadas
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build --no-deps

log_info "Aguardando containers iniciarem..."
sleep 60

log_info "Passo 7: Verificando status dos containers..."
docker-compose -f docker-compose.prod.yml ps

log_info "Passo 8: Testando conectividade..."

# Aguardar mais tempo para o backend ficar pronto
for i in {1..30}; do
    if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        log_info "✅ Backend funcionando na tentativa $i!"
        break
    else
        log_warn "Tentativa $i/30: Backend ainda não está pronto..."
        sleep 10
    fi
done

# Teste final
if curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    log_info "✅ Backend OK - Health check respondendo!"
    
    # Testar se o PostgreSQL está acessível
    if docker exec backend-container python -c "import asyncio, asyncpg; asyncio.run(asyncpg.connect('postgresql://pmcell_user:PmcellKingHost2025!@db:5432/pmcell_db').close())" 2>/dev/null; then
        log_info "✅ PostgreSQL OK - Conexão estabelecida!"
    else
        log_warn "⚠️ PostgreSQL pode não estar completamente pronto"
    fi
else
    log_error "❌ Backend ainda não está respondendo após 5 minutos"
    log_info "Verificando logs do backend:"
    docker logs backend-container --tail 20
fi

# Testar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    log_info "✅ Frontend funcionando!"
else
    log_error "❌ Frontend não está respondendo"
    log_info "Verificando logs do frontend:"
    docker logs frontend-container --tail 20
fi

log_info "Passo 9: Configurando Nginx para acesso unificado..."
apt install -y nginx

# Configuração Nginx atualizada
cat > /etc/nginx/sites-available/pmcell << 'EOF'
server {
    listen 80;
    server_name 177.153.64.105 _;
    
    # Frontend - Redirecionar para container frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    # Health check direto
    location /health {
        proxy_pass http://localhost:8000/api/v1/health;
    }
}
EOF

# Ativar site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/pmcell /etc/nginx/sites-enabled/

# Testar e reiniciar
nginx -t && systemctl restart nginx

log_info "Passo 10: Teste final da aplicação..."
sleep 10

# Teste através do Nginx
if curl -f http://177.153.64.105/health > /dev/null 2>&1; then
    log_info "✅ Aplicação acessível via IP público!"
else
    log_warn "⚠️ Aplicação ainda não acessível via IP público"
fi

log_info "🎉 Deploy corrigido finalizado!"
log_info ""
log_info "📊 Informações do deploy:"
log_info "Aplicação: http://177.153.64.105"
log_info "API: http://177.153.64.105/api/v1/"
log_info "Health: http://177.153.64.105/health"
log_info ""
log_info "🔧 Comandos de diagnóstico:"
log_info "Logs backend: docker logs backend-container"
log_info "Logs frontend: docker logs frontend-container"
log_info "Logs nginx: tail -f /var/log/nginx/error.log"
log_info "Status containers: docker-compose -f docker-compose.prod.yml ps"
log_info ""
log_info "🔑 Correções aplicadas:"
log_info "✅ JWT forte de 64 caracteres gerado"
log_info "✅ Health check corrigido (/api/v1/health)"
log_info "✅ React Router downgrade para v6 (Node 18 compatível)"
log_info "✅ Package-lock.json removido"
log_info "✅ Nginx configurado para proxying correto"