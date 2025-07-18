#!/bin/bash

# Script Simplificado de Deploy PMCELL
# Execute no servidor: bash deploy-simples.sh

echo "🚀 Deploy Simplificado PMCELL..."

# 1. Verificar status atual
echo "=== Status Atual ==="
docker-compose -f docker-compose.prod.yml ps
echo ""

# 2. Parar tudo
echo "=== Parando containers ==="
docker-compose -f docker-compose.prod.yml down
docker container prune -f

# 3. Gerar JWT forte
echo "=== Gerando JWT forte ==="
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
echo "✅ JWT configurado!"

# 4. Corrigir health check
echo "=== Corrigindo health check ==="
sed -i 's|http://localhost:8000/health|http://localhost:8000/api/v1/health|g' backend/Dockerfile
echo "✅ Health check corrigido!"

# 5. Corrigir React Router
echo "=== Corrigindo React Router ==="
sed -i 's|"react-router-dom": ".*"|"react-router-dom": "^6.26.1"|g' frontend/package.json
rm -f frontend/package-lock.json
echo "✅ React Router corrigido!"

# 6. Rebuild completo
echo "=== Fazendo rebuild ==="
docker-compose -f docker-compose.prod.yml --env-file .env.prod build --no-cache

# 7. Subir containers
echo "=== Subindo containers ==="
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 8. Aguardar e testar
echo "=== Aguardando containers ==="
sleep 60

echo "=== Status Final ==="
docker-compose -f docker-compose.prod.yml ps

echo "=== Testando Backend ==="
for i in {1..10}; do
    if curl -f http://localhost:8000/api/v1/health 2>/dev/null; then
        echo "✅ Backend OK na tentativa $i!"
        break
    else
        echo "⏳ Tentativa $i/10..."
        sleep 10
    fi
done

echo "=== Testando Frontend ==="
if curl -f http://localhost:3000 2>/dev/null; then
    echo "✅ Frontend OK!"
else
    echo "❌ Frontend com problemas"
    echo "Logs do frontend:"
    docker logs frontend-container --tail 10
fi

echo "=== Configurando Nginx ==="
apt install -y nginx

cat > /etc/nginx/sites-available/pmcell << 'EOF'
server {
    listen 80;
    server_name 177.153.64.105 _;
    
    # Frontend
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
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/api/v1/health;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/pmcell /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

echo "=== Teste Final ==="
sleep 10
if curl -f http://177.153.64.105/health 2>/dev/null; then
    echo "🎉 SUCESSO! Aplicação online em http://177.153.64.105"
else
    echo "❌ Ainda com problemas. Diagnóstico:"
    echo "Backend logs:"
    docker logs backend-container --tail 5
    echo "Frontend logs:"
    docker logs frontend-container --tail 5
    echo "Nginx status:"
    systemctl status nginx --no-pager
fi