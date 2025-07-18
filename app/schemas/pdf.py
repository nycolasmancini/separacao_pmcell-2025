"""
Schemas Pydantic para upload e processamento de PDFs.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


def normalize_logistics_type(logistics_type: str) -> str:
    """
    Normaliza o tipo de logística para o formato aceito pelo backend.
    
    Args:
        logistics_type: Tipo de logística (display ou normalizado)
        
    Returns:
        Tipo normalizado em lowercase com underscores
    """
    if not logistics_type:
        return logistics_type
    
    # Mapeamento de valores de display para valores normalizados
    logistics_mapping = {
        'lalamove': 'lalamove',
        'correios': 'correios', 
        'melhor envio': 'melhor_envio',
        'retirada': 'retirada',
        'entrega': 'entrega',
        'cliente na loja': 'cliente_na_loja',
        'ônibus': 'onibus',
        'onibus': 'onibus',  # Fallback sem acento
        # Valores já normalizados
        'melhor_envio': 'melhor_envio',
        'cliente_na_loja': 'cliente_na_loja'
    }
    
    normalized = logistics_type.lower().strip()
    return logistics_mapping.get(normalized, normalized)


def normalize_package_type(package_type: str) -> str:
    """
    Normaliza o tipo de embalagem para o formato aceito pelo backend.
    
    Args:
        package_type: Tipo de embalagem (display ou normalizado)
        
    Returns:
        Tipo normalizado em lowercase
    """
    if not package_type:
        return package_type
    
    # Mapeamento de valores de display para valores normalizados
    package_mapping = {
        'caixa': 'caixa',
        'sacola': 'sacola'
    }
    
    normalized = package_type.lower().strip()
    return package_mapping.get(normalized, normalized)


class PDFItemCreate(BaseModel):
    """Schema para item extraído do PDF."""
    product_code: str = Field(..., description="Código do produto")
    product_reference: str = Field(..., description="Referência do produto")
    product_name: str = Field(..., description="Nome do produto")
    quantity: int = Field(..., gt=0, description="Quantidade")
    unit_price: float = Field(..., gt=0, description="Preço unitário")
    total_price: float = Field(..., gt=0, description="Preço total")
    
    @validator('product_name', 'product_reference')
    def clean_text_fields(cls, v):
        """Remove espaços extras dos campos de texto."""
        return v.strip() if v else v
    
    @validator('total_price')
    def validate_total_price(cls, v, values):
        """Valida se o preço total está correto."""
        if 'quantity' in values and 'unit_price' in values:
            expected_total = values['quantity'] * values['unit_price']
            # Validação rigorosa - deve ser exato (tolerância de apenas R$ 0.01 para arredondamento)
            if abs(v - expected_total) > 0.01:
                raise ValueError(
                    f"Total price mismatch: expected {expected_total:.2f}, got {v:.2f}. "
                    f"Difference: {abs(v - expected_total):.2f}"
                )
        return v


class PDFExtractedData(BaseModel):
    """Schema para dados extraídos do PDF."""
    order_number: str = Field(..., description="Número do orçamento")
    client_name: str = Field(..., min_length=1, description="Nome do cliente")
    seller_name: str = Field(..., min_length=1, description="Nome do vendedor")
    order_date: datetime = Field(..., description="Data do pedido")
    total_value: float = Field(..., gt=0, description="Valor total do pedido")
    items: List[PDFItemCreate] = Field(..., min_items=1, description="Lista de itens")
    
    @validator('items')
    def validate_items_total(cls, v, values):
        """Valida se a soma dos itens confere com o valor total."""
        if 'total_value' in values and v:
            items_total = sum(item.total_price for item in v)
            expected_total = values['total_value']
            # Validação rigorosa - deve ser exato (tolerância de apenas R$ 0.01 para arredondamento)
            if abs(items_total - expected_total) > 0.01:
                raise ValueError(
                    f"Items total ({items_total:.2f}) doesn't match order total ({expected_total:.2f}). "
                    f"Difference: {abs(items_total - expected_total):.2f}"
                )
        return v
    
    @property
    def items_count(self) -> int:
        """Retorna quantidade total de itens (soma das quantidades)."""
        return sum(item.quantity for item in self.items)
    
    @property
    def models_count(self) -> int:
        """Retorna quantidade de modelos diferentes (quantidade de linhas)."""
        return len(self.items)
    
    @property
    def calculated_total(self) -> float:
        """Retorna valor total calculado (soma dos totais dos itens)."""
        return sum(item.total_price for item in self.items)


class PDFUploadRequest(BaseModel):
    """Schema para request de upload de PDF."""
    logistics_type: Optional[str] = Field(None, description="Tipo de logística")
    package_type: Optional[str] = Field(None, description="Tipo de embalagem")
    observations: Optional[str] = Field(None, max_length=500, description="Observações")
    
    @validator('logistics_type')
    def validate_logistics_type(cls, v):
        """Valida tipo de logística."""
        if v is not None:
            normalized = normalize_logistics_type(v)
            allowed_types = [
                'lalamove', 'correios', 'melhor_envio', 
                'retirada', 'entrega', 'cliente_na_loja', 'onibus'
            ]
            if normalized not in allowed_types:
                raise ValueError(f"Invalid logistics type. Allowed: {allowed_types}")
            return normalized
        return v
    
    @validator('package_type')
    def validate_package_type(cls, v):
        """Valida tipo de embalagem."""
        if v is not None:
            normalized = normalize_package_type(v)
            allowed_types = ['caixa', 'sacola']
            if normalized not in allowed_types:
                raise ValueError(f"Invalid package type. Allowed: {allowed_types}")
            return normalized
        return v


class PDFPreviewResponse(BaseModel):
    """Schema para response do preview dos dados extraídos."""
    success: bool = Field(..., description="Se a extração foi bem-sucedida")
    message: str = Field(..., description="Mensagem de status")
    data: Optional[PDFExtractedData] = Field(None, description="Dados extraídos")
    errors: Optional[List[str]] = Field(None, description="Lista de erros encontrados")
    
    # Informações para validação do vendedor
    validation_info: Optional[dict] = Field(None, description="Informações para validação")
    
    @property
    def summary(self) -> Optional[dict]:
        """Retorna resumo para validação do vendedor."""
        if not self.data:
            return None
        
        return {
            "calculated_total": self.data.calculated_total,
            "pdf_total": self.data.total_value,
            "items_count": self.data.items_count,
            "models_count": self.data.models_count,
            "totals_match": abs(self.data.calculated_total - self.data.total_value) <= 0.01
        }
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "PDF processado com sucesso",
                "data": {
                    "order_number": "12345",
                    "client_name": "EMPRESA TESTE LTDA",
                    "seller_name": "João Silva",
                    "order_date": "2024-07-12T00:00:00",
                    "total_value": 1250.00,
                    "items": [
                        {
                            "product_code": "001",
                            "product_reference": "REF-001",
                            "product_name": "PRODUTO TESTE 1",
                            "quantity": 5,
                            "unit_price": 100.00,
                            "total_price": 500.00
                        }
                    ]
                },
                "errors": None
            }
        }


class OrderCreateFromPDF(BaseModel):
    """Schema para criação de pedido a partir do PDF."""
    pdf_data: PDFExtractedData = Field(..., description="Dados extraídos do PDF")
    logistics_type: Optional[str] = Field(None, description="Tipo de logística")
    package_type: Optional[str] = Field(None, description="Tipo de embalagem")
    observations: Optional[str] = Field(None, max_length=500, description="Observações")
    
    @validator('logistics_type')
    def validate_logistics_type(cls, v):
        """Valida tipo de logística."""
        if v is not None:
            normalized = normalize_logistics_type(v)
            allowed_types = [
                'lalamove', 'correios', 'melhor_envio', 
                'retirada', 'entrega', 'cliente_na_loja', 'onibus'
            ]
            if normalized not in allowed_types:
                raise ValueError(f"Invalid logistics type. Allowed: {allowed_types}")
            return normalized
        return v
    
    @validator('package_type')
    def validate_package_type(cls, v):
        """Valida tipo de embalagem."""
        if v is not None:
            normalized = normalize_package_type(v)
            allowed_types = ['caixa', 'sacola']
            if normalized not in allowed_types:
                raise ValueError(f"Invalid package type. Allowed: {allowed_types}")
            return normalized
        return v


class OrderResponse(BaseModel):
    """Schema para response de criação de pedido."""
    id: int = Field(..., description="ID do pedido criado")
    order_number: str = Field(..., description="Número do orçamento")
    client_name: str = Field(..., description="Nome do cliente")
    seller_name: str = Field(..., description="Nome do vendedor")
    total_value: float = Field(..., description="Valor total")
    items_count: int = Field(..., description="Quantidade total de itens")
    progress_percentage: float = Field(..., description="Porcentagem de progresso")
    created_at: datetime = Field(..., description="Data de criação")
    
    class Config:
        from_attributes = True