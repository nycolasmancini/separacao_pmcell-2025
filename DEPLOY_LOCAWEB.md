# 🚀 Deploy PMCELL na Locaweb - Passo a Passo Completo

## 💰 Custo Total: R$ 15,90/mês

## 📋 Pré-requisitos

1. **Cartão de crédito** ou conta para Pix/Boleto
2. **CPF** para cadastro
3. **Email** válido
4. **Código do projeto** pronto para deploy

---

## 🛒 **PASSO 1: Contratar VPS na Locaweb**

### 1.1. Acessar site da Locaweb
```
1. Abra: https://www.locaweb.com.br/servidor-vps/
2. Clique em "VPS Linux" 
3. Escolha o plano de R$ 15,90/mês
```

### 1.2. Configurar VPS
```
Configuração recomendada:
- Sistema: Ubuntu 22.04 LTS
- Localização: São Paulo
- Nome do servidor: pmcell-vps
- Senha root: (criar uma senha forte)
```

### 1.3. Finalizar compra
```
1. Preencher dados pessoais
2. Escolher forma de pagamento (Pix é instantâneo)
3. Confirmar compra
4. Aguardar email com dados de acesso (~5-15 minutos)
```

### 1.4. Email de confirmação
```
Você receberá:
- IP do servidor: xxx.xxx.xxx.xxx
- Usuário: root
- Senha: (a que você definiu)
- Painel de controle: https://painel.locaweb.com.br
```

---

## 🖥️ **PASSO 2: Acessar VPS via SSH**

### 2.1. Windows (PowerShell/Terminal)
```powershell
# Abrir PowerShell como administrador
ssh root@SEU_IP_DO_VPS

# Exemplo:
ssh root@186.202.123.456

# Digite a senha quando solicitado
```

### 2.2. Mac/Linux (Terminal)
```bash
# Abrir Terminal
ssh root@SEU_IP_DO_VPS

# Se der erro de permissão:
ssh -o StrictHostKeyChecking=no root@SEU_IP_DO_VPS
```

### 2.3. Primeiro acesso
```bash
# Após conectar, atualize o sistema:
apt update && apt upgrade -y

# Criar usuário não-root (recomendado)
adduser pmcell
usermod -aG sudo pmcell

# Mas vamos continuar como root por simplicidade
```

---

## 🐳 **PASSO 3: Instalar Docker**

### 3.1. Instalar Docker
```bash
# Remover versões antigas
apt-get remove docker docker-engine docker.io containerd runc

# Instalar dependências
apt-get update
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Adicionar chave GPG oficial do Docker
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adicionar repositório
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
docker --version
```

### 3.2. Instalar Docker Compose
```bash
# Baixar Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

---

## 📦 **PASSO 4: Preparar Código**

### 4.1. Instalar Git
```bash
apt-get install -y git
```

### 4.2. Criar diretório do projeto
```bash
# Criar diretório
mkdir -p /opt/pmcell
cd /opt/pmcell
```

### 4.3. Opção A: Clonar do GitHub (se você já fez upload)
```bash
# Clonar repositório
git clone https://github.com/SEU_USUARIO/pmcell-separacao.git .

# Ou se for privado:
git clone https://SEU_TOKEN@github.com/SEU_USUARIO/pmcell-separacao.git .
```

### 4.3. Opção B: Upload manual via SFTP
```bash
# No seu computador local, use FileZilla ou WinSCP:
# Host: SEU_IP_DO_VPS
# Usuário: root
# Senha: sua_senha
# Porta: 22

# Fazer upload de todos os arquivos para /opt/pmcell
```

### 4.3. Opção C: Transferir via SCP
```bash
# No seu computador local:
cd /Users/nycolasmancini/Desktop/pmcell-separacao

# Compactar projeto
tar -czf pmcell.tar.gz .

# Enviar para servidor
scp pmcell.tar.gz root@SEU_IP_DO_VPS:/opt/pmcell/

# No servidor, descompactar:
cd /opt/pmcell
tar -xzf pmcell.tar.gz
rm pmcell.tar.gz
```

---

## ⚙️ **PASSO 5: Configurar Ambiente**

### 5.1. Criar arquivo de ambiente
```bash
cd /opt/pmcell

# Criar arquivo de produção
cat > .env.prod << 'EOF'
# Database
DB_USER=pmcell_user
DB_PASSWORD=SuaSenhaSegura123!
DB_NAME=pmcell_db
DB_HOST=db

# App
JWT_SECRET_KEY=pmcell-jwt-secret-key-producao-2025
ADMIN_PASSWORD=thmpv321
ENVIRONMENT=production
DEBUG=False

# URLs (substitua pelo seu IP)
FRONTEND_URL=http://SEU_IP_DO_VPS
BACKEND_URL=http://SEU_IP_DO_VPS:8000

# Database URL completa
DATABASE_URL=postgresql+asyncpg://pmcell_user:SuaSenhaSegura123!@db:5432/pmcell_db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
ALLOWED_ORIGINS=http://SEU_IP_DO_VPS
EOF

# Substituir SEU_IP_DO_VPS pelo IP real
sed -i "s/SEU_IP_DO_VPS/$(curl -s ifconfig.me)/g" .env.prod

# Verificar arquivo
cat .env.prod
```

### 5.2. Ajustar permissões
```bash
chmod 600 .env.prod
```

---

## 🚀 **PASSO 6: Deploy com Docker**

### 6.1. Build e iniciar containers
```bash
# Garantir que estamos no diretório correto
cd /opt/pmcell

# Parar qualquer container rodando
docker-compose down

# Build e iniciar em produção
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

# Aguardar ~2-3 minutos para tudo iniciar
```

### 6.2. Verificar status
```bash
# Ver containers rodando
docker-compose -f docker-compose.prod.yml ps

# Deve mostrar:
# pmcell-db-prod       running
# pmcell-backend-prod  running  
# pmcell-frontend-prod running
# pmcell-redis-prod    running

# Ver logs
docker-compose -f docker-compose.prod.yml logs --tail=50
```

### 6.3. Testar backend
```bash
# Testar health check
curl http://localhost:8000/health

# Resposta esperada:
# {"status":"healthy","service":"PMCELL - Separação de Pedidos"...}
```

---

## 🌐 **PASSO 7: Configurar Nginx**

### 7.1. Instalar Nginx
```bash
apt-get install -y nginx
```

### 7.2. Criar configuração
```bash
# Remover configuração padrão
rm /etc/nginx/sites-enabled/default

# Criar nova configuração
cat > /etc/nginx/sites-available/pmcell << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        proxy_pass http://localhost:80;
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
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
EOF

# Ativar site
ln -s /etc/nginx/sites-available/pmcell /etc/nginx/sites-enabled/

# Testar configuração
nginx -t

# Reiniciar Nginx
systemctl restart nginx
```

### 7.3. Ajustar Docker ports
```bash
# Editar docker-compose.prod.yml para não expor portas diretamente
# O Nginx fará o proxy
```

---

## 🧪 **PASSO 8: Testar Aplicação**

### 8.1. Acessar no navegador
```
1. Abra seu navegador
2. Digite: http://SEU_IP_DO_VPS
3. Deve aparecer a tela de login do PMCELL
```

### 8.2. Fazer login de teste
```
PIN padrão: 1234
```

### 8.3. Verificar funcionalidades
```
- Login funciona
- Dashboard carrega
- Criar novo pedido
- Separar itens
```

---

## 🔒 **PASSO 9: Segurança e Backup**

### 9.1. Configurar firewall
```bash
# Instalar ufw
apt-get install -y ufw

# Configurar regras
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS (futuro)

# Ativar firewall
ufw --force enable

# Verificar status
ufw status
```

### 9.2. Configurar backup automático
```bash
# Criar script de backup
cat > /opt/backup-pmcell.sh << 'EOF'
#!/bin/bash
cd /opt/pmcell
./scripts/backup.sh
EOF

chmod +x /opt/backup-pmcell.sh

# Agendar backup diário às 2 da manhã
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/backup-pmcell.sh") | crontab -
```

### 9.3. Criar primeiro backup
```bash
cd /opt/pmcell
./scripts/backup.sh
```

---

## 🎯 **PASSO 10: Otimizações Finais**

### 10.1. Configurar restart automático
```bash
# Criar serviço systemd
cat > /etc/systemd/system/pmcell.service << 'EOF'
[Unit]
Description=PMCELL Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/pmcell
ExecStart=/usr/local/bin/docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
ExecStop=/usr/local/bin/docker-compose -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Ativar serviço
systemctl enable pmcell
systemctl start pmcell
```

### 10.2. Monitoramento simples
```bash
# Script de monitoramento
cat > /opt/check-pmcell.sh << 'EOF'
#!/bin/bash
if ! curl -f http://localhost/health > /dev/null 2>&1; then
    echo "PMCELL is down! Restarting..."
    cd /opt/pmcell
    docker-compose -f docker-compose.prod.yml restart
fi
EOF

chmod +x /opt/check-pmcell.sh

# Executar a cada 5 minutos
(crontab -l 2>/dev/null; echo "*/5 * * * * /opt/check-pmcell.sh") | crontab -
```

---

## ✅ **Checklist Final**

- [ ] VPS Locaweb contratado e pago
- [ ] SSH funcionando
- [ ] Docker instalado
- [ ] Código no servidor
- [ ] Variáveis de ambiente configuradas
- [ ] Docker Compose rodando
- [ ] Nginx configurado
- [ ] Aplicação acessível via navegador
- [ ] Login funcionando
- [ ] Backup configurado
- [ ] Firewall ativo

---

## 🆘 **Troubleshooting**

### Problema: Não consigo acessar via SSH
```bash
# No painel da Locaweb, reinicie o VPS
# Verifique se o IP está correto
# Tente com outro cliente SSH
```

### Problema: Docker não instala
```bash
# Verificar versão do Ubuntu
lsb_release -a

# Se não for 22.04, ajustar comandos
```

### Problema: Site não abre
```bash
# Verificar se containers estão rodando
docker ps

# Ver logs
docker-compose -f docker-compose.prod.yml logs

# Testar localmente
curl http://localhost
```

### Problema: Erro de banco de dados
```bash
# Verificar se PostgreSQL está rodando
docker-compose -f docker-compose.prod.yml ps db

# Ver logs do banco
docker-compose -f docker-compose.prod.yml logs db

# Recriar banco se necessário
docker-compose -f docker-compose.prod.yml down -v
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🎉 **Pronto!**

Sua aplicação PMCELL está rodando em produção na Locaweb!

- **URL**: http://SEU_IP_DO_VPS
- **Custo**: R$ 15,90/mês
- **Capacidade**: 10-20 usuários simultâneos

**Próximos passos opcionais:**
1. Configurar domínio próprio
2. Adicionar SSL com Let's Encrypt
3. Configurar CDN para assets
4. Adicionar monitoramento avançado

---

**Precisa de ajuda?** Me avise em qual passo está com dificuldade!