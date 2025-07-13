#!/bin/bash

echo "🚀 Iniciando PMCELL - Separação de Pedidos"
echo "=========================================="

# Verificar se estamos no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Execute este script no diretório raiz do projeto!"
    exit 1
fi

# Função para iniciar com Docker
start_docker() {
    echo "🐳 Iniciando com Docker..."
    docker-compose up -d
    
    echo "✅ Containers iniciados!"
    echo ""
    echo "📱 URLs de Acesso:"
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔙 Backend API: http://localhost:8000"
    echo "📚 Documentação: http://localhost:8000/docs"
    echo ""
    echo "🔑 PINs de Acesso:"
    echo "1234 - Administrador"
    echo "5678 - Vendedor Teste"
    echo "9012 - Separador Teste"
    echo "3456 - Comprador Teste"
    echo "0000 - Super Admin"
}

# Função para iniciar manualmente
start_manual() {
    echo "⚙️  Iniciando manualmente..."
    
    # Backend
    echo "🐍 Iniciando Backend..."
    cd backend
    source venv/bin/activate
    python3 -c "
import asyncio
from app.core.database import Base, engine
from app.core.config import settings

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Tabelas criadas')

asyncio.run(create_tables())
" 2>/dev/null

    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Aguardar backend iniciar
    sleep 3
    
    # Frontend
    echo "⚛️  Iniciando Frontend..."
    cd frontend
    # Instalar dependências se necessário
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Serviços iniciados!"
    echo ""
    echo "📱 URLs de Acesso:"
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔙 Backend API: http://localhost:8000"
    echo "📚 Documentação: http://localhost:8000/docs"
    echo ""
    echo "🔑 PINs de Acesso:"
    echo "1234 - Administrador"
    echo "5678 - Vendedor Teste"
    echo "9012 - Separador Teste"
    echo "3456 - Comprador Teste"
    echo "0000 - Super Admin"
    echo ""
    echo "Para parar: kill $BACKEND_PID $FRONTEND_PID"
    
    # Aguardar finalização
    wait
}

# Menu de opções
echo "Escolha o método de execução:"
echo "1) Docker (Recomendado)"
echo "2) Manual (Desenvolvimento)"
echo ""
read -p "Digite sua opção (1 ou 2): " option

case $option in
    1)
        start_docker
        ;;
    2)
        start_manual
        ;;
    *)
        echo "❌ Opção inválida!"
        exit 1
        ;;
esac