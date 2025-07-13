#!/usr/bin/env python3
"""
Script para ativar usuários no banco de dados.
Útil quando um usuário está com is_active=False e não consegue acessar o sistema.

Uso:
    python scripts/activate_user.py --name "Nome do Usuário"
    python scripts/activate_user.py --pin "1234"
    python scripts/activate_user.py --all  # Ativa todos os usuários
"""
import asyncio
import argparse
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from app.core.database import get_async_session
from app.models.user import User


async def activate_user_by_name(name: str):
    """Ativa um usuário específico pelo nome."""
    async for session in get_async_session():
        # Buscar usuário
        result = await session.execute(
            select(User).where(User.name == name)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ Usuário '{name}' não encontrado.")
            return False
        
        if user.is_active:
            print(f"✅ Usuário '{name}' já está ativo.")
            return True
        
        # Ativar usuário
        user.is_active = True
        await session.commit()
        
        print(f"✅ Usuário '{name}' foi ativado com sucesso!")
        return True


async def activate_user_by_pin(pin: str):
    """Ativa um usuário específico pelo PIN."""
    async for session in get_async_session():
        # Buscar todos os usuários
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        # Verificar PIN (precisa importar a função de verificação)
        from app.core.security import verify_password
        
        user_found = None
        for user in users:
            if verify_password(pin, user.pin_hash):
                user_found = user
                break
        
        if not user_found:
            print(f"❌ Nenhum usuário encontrado com o PIN fornecido.")
            return False
        
        if user_found.is_active:
            print(f"✅ Usuário '{user_found.name}' já está ativo.")
            return True
        
        # Ativar usuário
        user_found.is_active = True
        await session.commit()
        
        print(f"✅ Usuário '{user_found.name}' foi ativado com sucesso!")
        return True


async def activate_all_users():
    """Ativa todos os usuários inativos."""
    async for session in get_async_session():
        # Buscar usuários inativos
        result = await session.execute(
            select(User).where(User.is_active == False)
        )
        inactive_users = result.scalars().all()
        
        if not inactive_users:
            print("✅ Todos os usuários já estão ativos.")
            return True
        
        # Ativar todos
        for user in inactive_users:
            user.is_active = True
            print(f"  ➜ Ativando usuário '{user.name}'...")
        
        await session.commit()
        
        print(f"\n✅ {len(inactive_users)} usuário(s) ativado(s) com sucesso!")
        return True


async def list_users():
    """Lista todos os usuários e seus status."""
    async for session in get_async_session():
        result = await session.execute(
            select(User).order_by(User.name)
        )
        users = result.scalars().all()
        
        print("\n📋 Lista de Usuários:")
        print("-" * 60)
        print(f"{'Nome':<20} {'Role':<15} {'Status':<10} {'Criado em'}")
        print("-" * 60)
        
        for user in users:
            status = "✅ Ativo" if user.is_active else "❌ Inativo"
            created = user.created_at.strftime("%d/%m/%Y")
            print(f"{user.name:<20} {user.role.value:<15} {status:<10} {created}")
        
        print("-" * 60)
        print(f"Total: {len(users)} usuários\n")


async def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Ativa usuários no sistema PMCELL"
    )
    
    parser.add_argument(
        "--name", "-n",
        help="Nome do usuário a ser ativado"
    )
    parser.add_argument(
        "--pin", "-p",
        help="PIN do usuário a ser ativado"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Ativa todos os usuários inativos"
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="Lista todos os usuários e seus status"
    )
    
    args = parser.parse_args()
    
    # Validar argumentos
    if not any([args.name, args.pin, args.all, args.list]):
        parser.print_help()
        print("\n❌ Erro: Você deve especificar pelo menos uma opção.")
        sys.exit(1)
    
    try:
        if args.list:
            await list_users()
        elif args.name:
            await activate_user_by_name(args.name)
        elif args.pin:
            await activate_user_by_pin(args.pin)
        elif args.all:
            await activate_all_users()
    
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    print("🔧 PMCELL - Ativação de Usuários")
    print("=" * 40)
    asyncio.run(main())