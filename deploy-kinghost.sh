#!/bin/bash

# Script de Deploy PMCELL na KingHost
# Execute no servidor VPS como root

set -e  # Sair se houver erro

echo "🚀 Iniciando deploy PMCELL na KingHost..."

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

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.prod.yml" ]; then
    log_error "Arquivo docker-compose.prod.yml não encontrado. Execute no diretório do projeto."
    exit 1
fi

log_info "Passo 1: Descompactando código..."
if [ -f "pmcell-deploy.tar.gz" ]; then
    tar -xzf pmcell-deploy.tar.gz
    rm pmcell-deploy.tar.gz
    log_info "Código descompactado com sucesso!"
else
    log_warn "Arquivo pmcell-deploy.tar.gz não encontrado, continuando..."
fi

log_info "Passo 2: Atualizando sistema..."
apt update && apt upgrade -y
apt install -y curl wget git nano htop ufw

log_info "Passo 3: Instalando Docker..."
# Remover versões antigas
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

# Instalar dependências
apt-get install -y ca-certificates curl gnupg lsb-release

# Adicionar chave GPG do Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adicionar repositório
echo "deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
docker --version

log_info "Passo 4: Instalando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-\$(uname -s)-\$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
docker-compose --version

log_info "Passo 5: Configurando variáveis de ambiente..."
cat > .env.prod << 'EOF'
# Database
DB_USER=pmcell_user
DB_PASSWORD=PmcellKingHost2025!
DB_NAME=pmcell_db
DB_HOST=db

# App
JWT_SECRET_KEY=pmcell-kinghost-jwt-secret-2025-production
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
log_info "Variáveis de ambiente configuradas!"

log_info "Passo 6: Fazendo deploy da aplicação..."
# Parar containers existentes
docker-compose -f docker-compose.prod.yml down 2>/dev/null || true

# Iniciar aplicação
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

log_info "Aguardando containers iniciarem..."
sleep 30

# Verificar status
docker-compose -f docker-compose.prod.yml ps

log_info "Passo 7: Configurando Nginx..."
apt install -y nginx

# Criar configuração
cat > /etc/nginx/sites-available/pmcell << 'EOF'
server {
    listen 80;
    server_name 177.153.64.105 _;
    
    # Frontend
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
EOF

# Ativar site
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/pmcell /etc/nginx/sites-enabled/

# Testar e reiniciar
nginx -t && systemctl restart nginx

log_info "Passo 8: Configurando firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw --force enable

log_info "Passo 9: Testando aplicação..."
sleep 10

# Testar backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_info "✅ Backend funcionando!"
else
    log_error "❌ Backend não está respondendo"
fi

# Testar frontend
if curl -f http://localhost > /dev/null 2>&1; then
    log_info "✅ Frontend funcionando!"
else
    log_error "❌ Frontend não está respondendo"
fi

log_info "Passo 10: Configurando backup..."
cat > /opt/backup-pmcell.sh << 'EOF'
#!/bin/bash
cd /opt/pmcell
if [ -f "./scripts/backup.sh" ]; then
    ./scripts/backup.sh
else
    echo "Script de backup não encontrado"
fi
EOF

chmod +x /opt/backup-pmcell.sh

# Agendar backup diário
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-pmcell.sh") | crontab -

log_info "🎉 Deploy finalizado com sucesso!"
log_info ""
log_info "📊 Informações do deploy:"
log_info "Frontend: http://177.153.64.105"
log_info "Backend: http://177.153.64.105:8000"
log_info "Health: http://177.153.64.105/health"
log_info ""
log_info "🔧 Comandos úteis:"
log_info "Ver logs: docker-compose -f docker-compose.prod.yml logs -f"
log_info "Reiniciar: docker-compose -f docker-compose.prod.yml restart"
log_info "Status: docker-compose -f docker-compose.prod.yml ps"
log_info ""
log_info "🚀 Aplicação PMCELL está rodando!"