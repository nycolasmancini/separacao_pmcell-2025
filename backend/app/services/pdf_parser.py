"""
Serviço de parser de PDF para extração de dados de pedidos.

Este módulo é responsável por extrair informações de PDFs de pedidos
da PMCELL São Paulo, incluindo dados do cliente, vendedor, produtos e valores.
"""
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

import pdfplumber
import PyPDF2


logger = logging.getLogger(__name__)


class PDFParseError(Exception):
    """Exceção customizada para erros de parsing de PDF."""
    pass


class PDFParser:
    """
    Parser de PDF para extração de dados de pedidos.
    
    Utiliza pdfplumber como biblioteca principal e PyPDF2 como fallback.
    """
    
    # Patterns regex para extração de dados
    PATTERNS = {
        'order_number': r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
        'client': r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
        'seller': r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
        'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
        'total_value': r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
        'items': r'(\d{5})\s*/\s*([^/\n]+)\s*-->\s*([^/\n]+)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    }
    
    def extract(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extrai dados de um PDF de pedido.
        
        Args:
            pdf_path: Caminho para o arquivo PDF
            
        Returns:
            Dict contendo os dados extraídos
            
        Raises:
            PDFParseError: Se houver erro na extração
        """
        if not pdf_path.exists():
            raise PDFParseError(f"Arquivo não encontrado: {pdf_path}")
        
        if not str(pdf_path).lower().endswith('.pdf'):
            raise PDFParseError("Invalid PDF file")
        
        try:
            # Tenta extrair com pdfplumber primeiro
            text = self._extract_with_pdfplumber(pdf_path)
            if not text.strip():
                # Fallback para PyPDF2
                text = self._extract_with_pypdf2(pdf_path)
                
            if not text.strip():
                raise PDFParseError("Não foi possível extrair texto do PDF")
                
            # Extrai os dados usando patterns
            data = self._extract_data_from_text(text)
            
            # Valida os dados extraídos
            self.validate(data)
            
            return data
            
        except PDFParseError:
            raise
        except Exception as e:
            logger.error(f"Erro ao processar PDF: {str(e)}")
            raise PDFParseError(f"Erro ao processar PDF: {str(e)}")
    
    def _extract_with_pdfplumber(self, pdf_path: Path) -> str:
        """Extrai texto usando pdfplumber."""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text
        except Exception as e:
            logger.warning(f"Erro com pdfplumber: {e}")
            return ""
    
    def _extract_with_pypdf2(self, pdf_path: Path) -> str:
        """Extrai texto usando PyPDF2 como fallback."""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.warning(f"Erro com PyPDF2: {e}")
            return ""
    
    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto do PDF."""
        data = {
            'order_number': self._extract_with_pattern(text, 'order_number'),
            'client_name': self._clean_text(self._extract_with_pattern(text, 'client')),
            'seller_name': self._clean_text(self._extract_with_pattern(text, 'seller')),
            'order_date': self._parse_date(self._extract_with_pattern(text, 'date')),
            'total_value': self._parse_money_value(self._extract_with_pattern(text, 'total_value')),
            'items': self._extract_items(text)
        }
        
        return data
    
    def _extract_with_pattern(self, text: str, pattern_name: str) -> Optional[str]:
        """Extrai dados usando um pattern específico."""
        pattern = self.PATTERNS.get(pattern_name)
        if not pattern:
            return None
            
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extrai lista de itens do pedido."""
        items = []
        pattern = self.PATTERNS['items']
        
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            item = {
                'product_code': match.group(1).strip(),
                'product_reference': match.group(2).strip(),
                'product_name': match.group(3).strip(),
                'quantity': int(match.group(4)),
                'unit_price': self._parse_money_value(match.group(5)),
                'total_price': self._parse_money_value(match.group(6))
            }
            items.append(item)
            
        return items
    
    def _extract_items_from_line(self, line: str) -> List[Dict[str, Any]]:
        """Extrai item de uma linha específica (usado nos testes)."""
        return self._extract_items(line)
    
    def _parse_item_line(self, line: str) -> Dict[str, Any]:
        """Parse de uma linha de item (usado nos testes)."""
        items = self._extract_items_from_line(line)
        return items[0] if items else None
    
    def _parse_money_value(self, value: Optional[str]) -> Optional[float]:
        """
        Converte valor monetário brasileiro para float.
        
        Exemplos:
            "1.234,56" -> 1234.56
            "R$ 1.234,56" -> 1234.56
        """
        if not value:
            return None
            
        # Remove R$ e espaços
        value = value.replace('R$', '').strip()
        
        # Tratamento do formato brasileiro: 1.234,56
        # Se tem vírgula, é formato brasileiro
        if ',' in value:
            # Remove pontos (separador de milhar) e substitui vírgula por ponto
            value = value.replace('.', '').replace(',', '.')
        # Se não tem vírgula mas tem ponto, pode ser formato americano ou milhar brasileiro
        elif '.' in value:
            # Se tem mais de 3 dígitos após o último ponto, é milhar brasileiro sem centavos
            parts = value.split('.')
            if len(parts[-1]) > 2:
                # Formato: 1.234.567 (sem centavos)
                value = value.replace('.', '')
            # Senão, assume formato americano: 1234.56
        
        try:
            return float(value)
        except ValueError:
            return None
    
    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Converte data no formato brasileiro para datetime.
        
        Exemplo: "12/07/24" -> datetime(2024, 7, 12)
        """
        if not date_str:
            return None
            
        try:
            # Formato DD/MM/YY
            date_obj = datetime.strptime(date_str.strip(), "%d/%m/%y")
            
            # Ajusta ano para 20XX
            if date_obj.year < 100:
                date_obj = date_obj.replace(year=2000 + date_obj.year)
                
            return date_obj
        except ValueError:
            return None
    
    def _clean_text(self, text: Optional[str]) -> Optional[str]:
        """Limpa e normaliza campos de texto."""
        if not text:
            return None
            
        # Remove espaços extras e quebras de linha
        text = text.strip().replace('\n', ' ')
        
        # Remove prefixos comuns
        prefixes = ['Cliente:', 'CLIENTE:', 'Vendedor:', 'VENDEDOR:']
        for prefix in prefixes:
            if text.startswith(prefix):
                text = text[len(prefix):].strip()
                
        # Remove sufixos comuns (ex: "Forma" no campo cliente)
        suffixes = ['Forma', 'Validade']
        for suffix in suffixes:
            if suffix in text:
                text = text.split(suffix)[0].strip()
                
        return text
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Valida os dados extraídos.
        
        Args:
            data: Dados extraídos do PDF
            
        Returns:
            True se os dados são válidos
            
        Raises:
            PDFParseError: Se os dados são inválidos
        """
        # Campos obrigatórios
        required_fields = [
            'order_number', 'client_name', 'seller_name',
            'order_date', 'total_value', 'items'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                raise PDFParseError(f"Missing required field: {field}")
        
        # Validações específicas
        if not data['items']:
            raise PDFParseError("Order must have at least one item")
            
        if data['total_value'] <= 0:
            raise PDFParseError("Total value must be positive")
            
        # Valida cada item
        for i, item in enumerate(data['items']):
            required_item_fields = [
                'product_code', 'product_name', 'quantity',
                'unit_price', 'total_price'
            ]
            
            for field in required_item_fields:
                if field not in item or item[field] is None:
                    raise PDFParseError(f"Item {i} missing field: {field}")
                    
            if item['quantity'] <= 0:
                raise PDFParseError(f"Item {i} quantity must be positive")
                
        return True