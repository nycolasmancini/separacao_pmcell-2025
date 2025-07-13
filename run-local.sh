#!/bin/bash

echo "🚀 PMCELL - Execução Local (Desenvolvimento)"
echo "============================================"

# Verificar se estamos no diretório correto
if [ ! -f "package.json" ] && [ ! -f "frontend/package.json" ]; then
    echo "❌ Execute este script no diretório raiz do projeto!"
    exit 1
fi

# Função para parar serviços
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

echo "🔧 Verificando dependências..."

# Verificar e instalar dependências do backend
if [ ! -d "backend/venv" ]; then
    echo "📦 Criando ambiente virtual do Python..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Verificar e instalar dependências do frontend
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Instalando dependências do Node.js..."
    cd frontend
    npm install
    cd ..
fi

echo "🐍 Iniciando Backend..."
cd backend
source venv/bin/activate

# Criar tabelas se necessário
python3 -c "
import asyncio
import os
import sys
sys.path.append('.')

async def setup_db():
    try:
        from app.core.database import Base, engine
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print('✅ Banco de dados configurado')
        
        # Tentar popular com dados de teste
        try:
            from app.db.seed import create_users, create_sample_orders
            from app.core.database import get_async_session
            
            async for session in get_async_session():
                # Verificar se já tem dados
                from app.models.user import User
                from sqlalchemy import select
                result = await session.execute(select(User))
                users = result.scalars().all()
                
                if not users:
                    print('🌱 Populando banco com dados de teste...')
                    await create_users(session)
                    await create_sample_orders(session)
                    print('✅ Dados de teste criados')
                else:
                    print('ℹ️  Banco já contém dados')
                break
                
        except Exception as e:
            print(f'⚠️  Aviso: Não foi possível popular dados de teste: {e}')
            
    except Exception as e:
        print(f'❌ Erro ao configurar banco: {e}')

asyncio.run(setup_db())
"

# Iniciar backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

echo "⏳ Aguardando backend inicializar..."
sleep 3

# Verificar se backend está rodando
if curl -s http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "✅ Backend iniciado com sucesso!"
else
    echo "❌ Erro ao iniciar backend"
    cleanup
fi

echo "⚛️  Iniciando Frontend..."
cd frontend

# Atualizar vite.config.js para ambiente local
cat > vite.config.js << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '127.0.0.1',
    port: 5173,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
EOF

# Iniciar frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 PMCELL iniciado com sucesso!"
echo "================================"
echo ""
echo "📱 URLs de Acesso:"
echo "🌐 Frontend: http://127.0.0.1:5173"
echo "🔙 Backend API: http://127.0.0.1:8000"
echo "📚 Documentação: http://127.0.0.1:8000/docs"
echo ""
echo "🔑 PINs de Acesso:"
echo "1234 - Administrador"
echo "5678 - Vendedor Teste"
echo "9012 - Separador Teste"
echo "3456 - Comprador Teste"
echo "0000 - Super Admin"
echo ""
echo "💡 Para parar os serviços, pressione Ctrl+C"
echo ""

# Aguardar até o usuário parar
wait