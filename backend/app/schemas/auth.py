from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class LoginRequest(BaseModel):
    pin: str = Field(..., min_length=4, max_length=6, description="PIN do usuário")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    name: str
    role: str
    photo_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Nome do usuário")
    pin: str = Field(..., min_length=4, max_length=6, description="PIN do usuário")
    role: str = Field(..., description="Role do usuário (admin, seller, separator, buyer)")
    photo_url: Optional[str] = Field(None, description="URL da foto do usuário")
    
    @validator('role')
    def validate_role(cls, v):
        valid_roles = ['admin', 'seller', 'separator', 'buyer']
        if v not in valid_roles:
            raise ValueError(f'Role deve ser um dos seguintes: {", ".join(valid_roles)}')
        return v
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN deve conter apenas números')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nome do usuário")
    pin: Optional[str] = Field(None, min_length=4, max_length=6, description="PIN do usuário")
    role: Optional[str] = Field(None, description="Role do usuário (admin, seller, separator, buyer)")
    photo_url: Optional[str] = Field(None, description="URL da foto do usuário")
    
    @validator('role')
    def validate_role(cls, v):
        if v is not None:
            valid_roles = ['admin', 'seller', 'separator', 'buyer']
            if v not in valid_roles:
                raise ValueError(f'Role deve ser um dos seguintes: {", ".join(valid_roles)}')
        return v
    
    @validator('pin')
    def validate_pin(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError('PIN deve conter apenas números')
        return v

class OrderAccessRequest(BaseModel):
    order_id: int = Field(..., description="ID do pedido")
    pin: str = Field(..., min_length=4, max_length=6, description="PIN do usuário")

class OrderAccessResponse(BaseModel):
    success: bool
    user: UserResponse
    order_id: int
    message: str = "Acesso ao pedido autorizado"

# Evita import circular
TokenResponse.model_rebuild()