"""
Endpoints para gerenciamento de usuários (admin only).
"""
from typing import List, Optional
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_session, require_admin
from app.models.user import User, UserRole
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserUpdate, UserResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("", response_model=List[UserResponse])
async def list_users(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Lista todos os usuários (admin only).
    
    Args:
        session: Sessão do banco de dados
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        List[UserResponse]: Lista de usuários
    """
    try:
        user_repo = UserRepository(session)
        users = await user_repo.get_all()
        
        return [
            UserResponse(
                id=user.id,
                name=user.name,
                role=user.role,
                created_at=user.created_at,
                last_login=user.last_login
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error listing users for admin {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao listar usuários"
        )


@router.post("", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Cria um novo usuário (admin only).
    
    Args:
        user_data: Dados do usuário para criação
        session: Sessão do banco de dados
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        UserResponse: Dados do usuário criado
    """
    try:
        user_repo = UserRepository(session)
        
        # Verificar se já existe usuário com mesmo PIN
        existing_user = await user_repo.get_by_pin(user_data.pin)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Já existe um usuário com este PIN"
            )
        
        # Criar usuário
        user = await user_repo.create(
            name=user_data.name,
            pin=user_data.pin,
            role=user_data.role
        )
        
        logger.info(f"User created by admin {current_user.id}: {user.name} (ID: {user.id})")
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user for admin {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao criar usuário"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Busca usuário por ID (admin only).
    
    Args:
        user_id: ID do usuário
        session: Sessão do banco de dados
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        UserResponse: Dados do usuário
    """
    try:
        user_repo = UserRepository(session)
        user = await user_repo.get(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user {user_id} for admin {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao buscar usuário"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Atualiza usuário (admin only).
    
    Args:
        user_id: ID do usuário
        user_data: Dados para atualização
        session: Sessão do banco de dados
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        UserResponse: Dados do usuário atualizado
    """
    try:
        user_repo = UserRepository(session)
        user = await user_repo.get(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Verificar se PIN já está em uso por outro usuário
        if user_data.pin and user_data.pin != user.pin:
            existing_user = await user_repo.get_by_pin(user_data.pin)
            if existing_user and existing_user.id != user_id:
                raise HTTPException(
                    status_code=400,
                    detail="Já existe um usuário com este PIN"
                )
        
        # Atualizar campos
        if user_data.name:
            user.name = user_data.name
        if user_data.pin:
            user.set_pin(user_data.pin)
        if user_data.role:
            user.role = user_data.role
            
        await session.commit()
        
        logger.info(f"User {user_id} updated by admin {current_user.id}")
        
        return UserResponse(
            id=user.id,
            name=user.name,
            role=user.role,
            created_at=user.created_at,
            last_login=user.last_login
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user {user_id} for admin {current_user.id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao atualizar usuário"
        )


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(require_admin)
):
    """
    Remove usuário (admin only).
    
    Args:
        user_id: ID do usuário
        session: Sessão do banco de dados
        current_user: Usuário autenticado (deve ser admin)
        
    Returns:
        Dict com status da operação
    """
    try:
        user_repo = UserRepository(session)
        user = await user_repo.get(user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        
        # Não permitir que admin delete a si mesmo
        if user_id == current_user.id:
            raise HTTPException(
                status_code=400,
                detail="Não é possível deletar seu próprio usuário"
            )
        
        await user_repo.delete(user_id)
        await session.commit()
        
        logger.info(f"User {user_id} ({user.name}) deleted by admin {current_user.id}")
        
        return {
            "success": True,
            "message": f"Usuário {user.name} removido com sucesso"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id} for admin {current_user.id}: {str(e)}")
        await session.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao remover usuário"
        )