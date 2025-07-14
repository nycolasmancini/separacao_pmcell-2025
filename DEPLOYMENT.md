# 🚀 PMCELL - Deployment Guide

Complete deployment guide for the PMCELL order separation system.

## 📋 Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)
- Git

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   (React/Vite)  │◄──►│   (FastAPI)     │◄──►│ (PostgreSQL)    │
│   Port: 80      │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                               │
                    ┌─────────────────┐
                    │     Redis       │
                    │  (Cache/Queue)  │
                    │   Port: 6379    │
                    └─────────────────┘
```

## 🔧 Environment Setup

### 1. Environment Variables

Create environment files for your deployment target:

#### Production Backend (.env.production)
```bash
# App
APP_NAME="PMCELL - Separação de Pedidos"
APP_VERSION="1.0.0"
DEBUG=False
ENVIRONMENT=production

# Database (PostgreSQL)
DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:5432/${DB_NAME}

# Security
SECRET_KEY=${JWT_SECRET_KEY}
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Admin
ADMIN_PASSWORD=${ADMIN_PASSWORD}

# CORS
ALLOWED_ORIGINS=${FRONTEND_URL}

# Server
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Performance
MAX_CONNECTIONS=20
CONNECTION_TIMEOUT=30

# Caching (optional)
REDIS_URL=${REDIS_URL}
```

#### Production Frontend (.env.production)
```bash
VITE_API_URL=${BACKEND_URL}/api/v1
```

### 2. Required Secrets

The following secrets must be configured in your deployment platform:

| Variable | Description | Example |
|----------|-------------|---------|
| `JWT_SECRET_KEY` | Strong JWT signing key | `your-super-secure-jwt-secret-key-here` |
| `DB_PASSWORD` | Database password | `strong-database-password` |
| `ADMIN_PASSWORD` | Admin panel password | `thmpv321` |
| `FRONTEND_URL` | Frontend domain | `https://pmcell.railway.app` |
| `BACKEND_URL` | Backend domain | `https://pmcell-api.railway.app` |

## 🚂 Railway Deployment

### 1. Setup Railway Project

```bash
# Install Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login and create project
railway login
railway init
```

### 2. Deploy Services

#### Backend Service
```bash
# Create backend service
railway service create backend

# Set environment variables
railway variables set \
  SECRET_KEY="your-jwt-secret-key" \
  ADMIN_PASSWORD="thmpv321" \
  ALLOWED_ORIGINS="https://your-frontend-url.railway.app" \
  --service backend

# Deploy
railway up --service backend
```

#### Database Service
```bash
# Add PostgreSQL
railway add postgresql

# Get database URL
railway variables --service postgresql
```

#### Frontend Service
```bash
# Create frontend service
railway service create frontend

# Set environment variables
railway variables set \
  VITE_API_URL="https://your-backend-url.railway.app/api/v1" \
  --service frontend

# Deploy
railway up --service frontend
```

### 3. Domain Configuration (Optional)

```bash
# Add custom domain
railway domain add your-domain.com --service frontend
railway domain add api.your-domain.com --service backend
```

## 🎨 Render Deployment

### 1. Using render.yaml

Push the included `render.yaml` to your repository and connect it to Render.

### 2. Manual Setup

#### Database
1. Create PostgreSQL database
2. Note connection details

#### Backend
1. Create Web Service
2. Environment: Docker
3. Build Command: `docker build -f backend/Dockerfile .`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

#### Frontend
1. Create Static Site
2. Build Command: `npm run build`
3. Publish Directory: `dist`

## 🐳 Docker Deployment

### Development
```bash
# Start all services
docker-compose up --build

# Access services
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# Database: SQLite (file-based)
```

### Production
```bash
# Create environment file
cp .env.example .env.prod
# Edit .env.prod with production values

# Start production services
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Access services
# Frontend: http://localhost
# Backend: http://localhost:8000
# Database: PostgreSQL on port 5432
```

## 🔍 Health Checks

The application provides multiple health check endpoints:

| Endpoint | Purpose | Status Codes |
|----------|---------|--------------|
| `/health` | Basic health check | 200 |
| `/health/detailed` | Detailed with dependencies | 200/503 |
| `/ready` | Readiness probe | 200/503 |
| `/live` | Liveness probe | 200 |
| `/metrics` | Basic metrics | 200 |

Example health check:
```bash
curl -f http://your-domain.com/health
```

## 📊 Monitoring Setup

### Application Monitoring

The application includes built-in monitoring features:

1. **Health Checks**: Multiple endpoints for different monitoring needs
2. **Request Logging**: Structured JSON logs in production
3. **Security Monitoring**: Rate limiting and suspicious activity detection
4. **Performance Metrics**: Response times and database latencies

### External Monitoring (Recommended)

1. **Uptime Monitoring**: Use services like Pingdom or UptimeRobot
2. **Error Tracking**: Integrate Sentry (see Sentry section)
3. **Log Aggregation**: Use services like LogDNA or Papertrail

### Sentry Integration (Optional)

Add Sentry for error tracking:

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]

# Add to backend/requirements.txt
echo "sentry-sdk[fastapi]==1.32.0" >> backend/requirements.txt
```

Add to `backend/app/main.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration(auto_enable=True)],
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
    )
```

## 💾 Database Backup

### Automated Backups

Use the included backup script:

```bash
# Run backup manually
./scripts/backup.sh

# Setup automated backups (crontab)
crontab -e
# Add: 0 2 * * * /path/to/pmcell-separacao/scripts/backup.sh

# Test backup configuration
./scripts/backup.sh --test
```

### Manual Backup

#### PostgreSQL
```bash
pg_dump -h host -U user -d database > backup.sql
```

#### SQLite
```bash
cp pmcell.db backup_$(date +%Y%m%d).db
```

### Restore Database

```bash
# Interactive restore
./scripts/restore.sh

# Restore specific backup
./scripts/restore.sh /path/to/backup.sql.gz

# List available backups
./scripts/restore.sh --list
```

## 🛡️ Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong, unique passwords
- Rotate secrets regularly

### 2. Network Security
- Use HTTPS in production
- Configure firewall rules
- Limit database access

### 3. Application Security
- Rate limiting is enabled in production
- Security headers are automatically added
- Input validation is implemented
- SQL injection protection via SQLAlchemy

### 4. Database Security
- Use strong database passwords
- Enable database encryption at rest
- Regular security updates

## 🚨 Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check database connectivity
docker-compose logs backend

# Verify DATABASE_URL format
echo $DATABASE_URL
```

#### 2. CORS Issues
```bash
# Check ALLOWED_ORIGINS configuration
# Ensure frontend URL is included in CORS settings
```

#### 3. Build Failures
```bash
# Check Docker build logs
docker-compose logs --tail=100

# Clear Docker cache
docker system prune -a
```

#### 4. Memory Issues
```bash
# Check resource usage
docker stats

# Increase memory limits in docker-compose.yml
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Backend debug
DEBUG=True LOG_LEVEL=DEBUG docker-compose up backend

# Frontend debug
VITE_DEBUG=true npm run dev
```

### Log Analysis

```bash
# View application logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Search for errors
docker-compose logs backend | grep ERROR

# Check health status
curl -s http://localhost:8000/health/detailed | jq .
```

## 📈 Performance Optimization

### 1. Frontend Optimization
- Gzip compression enabled
- Asset caching configured
- Bundle splitting implemented
- Tree shaking enabled

### 2. Backend Optimization
- Connection pooling configured
- Redis caching (optional)
- Query optimization
- Rate limiting

### 3. Database Optimization
- Proper indexing
- Connection pooling
- Query optimization
- Regular maintenance

## 🔄 CI/CD Pipeline

The project includes GitHub Actions workflows:

### 1. Test Workflow (.github/workflows/test.yml)
- Runs on pull requests
- Backend and frontend tests
- Integration tests
- Security scans

### 2. Deploy Workflow (.github/workflows/deploy.yml)
- Triggers on main branch push
- Builds Docker images
- Deploys to Railway/Render
- Health checks

### 3. Security Workflow (.github/workflows/security.yml)
- Daily security scans
- Dependency checks
- Secret detection
- Container scanning

### GitHub Secrets Required

Configure these secrets in your GitHub repository:

| Secret | Description |
|--------|-------------|
| `RAILWAY_TOKEN` | Railway API token |
| `JWT_SECRET_KEY` | JWT signing key |
| `ADMIN_PASSWORD` | Admin panel password |
| `FRONTEND_URL` | Frontend domain |
| `BACKEND_URL` | Backend domain |
| `DATABASE_URL` | Database connection string |

## 📞 Support

### Getting Help

1. Check the logs first
2. Review this documentation
3. Check GitHub issues
4. Test with minimal configuration

### Maintenance Tasks

#### Weekly
- Review application logs
- Check health status
- Monitor resource usage

#### Monthly
- Update dependencies
- Review security alerts
- Backup verification
- Performance review

#### Quarterly
- Security audit
- Dependency updates
- Performance optimization
- Documentation updates

## 📝 Changelog

Keep track of deployments:

```bash
# Tag releases
git tag -a v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# Create release notes
# Document changes and deployment notes
```

---

For additional support or questions, please refer to the project documentation or create an issue in the repository.