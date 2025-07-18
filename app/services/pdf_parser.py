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
        # Padrão melhorado para itens - mantém compatibilidade
        'items': r'(?:^|\s)(\d{4,5})\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*(?:/\s*([^/]*?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    }
    
    # Padrões de fallback para casos específicos
    FALLBACK_PATTERNS = {
        'order_number': [
            r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
            r'Or[çc]amento\s*[-:]*\s*(\d+)',
            r'N[ºo°]\s*[:]*\s*(\d+)',
        ],
        'client': [
            r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
            r'Cliente\s*[-:]\s*([^\n]+?)(?:\s*Forma|$)',
            r'Cliente\s+([^\n]+?)(?:\s*Forma|$)',
        ],
        'seller': [
            r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
            r'Vendedor\s*[-:]\s*([^\n]+?)(?:\s*Validade|$)',
            r'Vendedor\s+([^\n]+?)(?:\s*Validade|$)',
        ],
        'date': [
            r'Data:\s*(\d{2}/\d{2}/\d{2})',
            r'Data\s*[-:]\s*(\d{2}/\d{2}/\d{2})',
            r'(\d{2}/\d{2}/\d{2})',
        ],
        'total_value': [
            r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
            r'TOTAL\s*R\$\s*([\d\.,]+)',
            r'VALOR\s*TOTAL\s*R\$\s*([\d\.,]+)',
        ],
        # Padrões específicos para itens com diferentes estruturas
        'items': [
            # Padrão principal atualizado (tolerante a variações)
            r'(?:^|\s)(\d{4,5})\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*(?:/\s*([^/]*?))?\s*/?<?/?<?\s*UN\s*/?\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
            # Padrão para formatação com /<<UN
            r'(?:^|\s)(\d{4,5})\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*/<<UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
            # Padrão para formatação com </< UN
            r'(?:^|\s)(\d{4,5})\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*</<\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
            # Padrão legacy para compatibilidade com PDFs antigos
            r'(\d+)\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*(?:/\s*([^/]*?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        ]
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
        # Normaliza texto para corrigir problemas de formatação
        normalized_text = self._normalize_text(text)
        # Para metadados, usa texto original; para itens, usa texto limpo
        cleaned_text = self._clean_extracted_text(normalized_text)
        
        data = {
            'order_number': self._extract_with_pattern(text, 'order_number'),
            'client_name': self._clean_text(self._extract_with_pattern(text, 'client')),
            'seller_name': self._clean_text(self._extract_with_pattern(text, 'seller')),
            'order_date': self._parse_date(self._extract_with_pattern(text, 'date')),
            'total_value': self._parse_money_value(self._extract_with_pattern(text, 'total_value')),
            'items': self._extract_items(cleaned_text)
        }
        
        return data
    
    def _normalize_text(self, text: str) -> str:
        """
        Normaliza texto extraído para corrigir problemas de formatação comum.
        """
        # Corrige variações problemáticas de formatação de itens
        text = text.replace('/<<UN', ' / UN ')   # Corrige /<<UN para / UN (sem dupla barra)
        text = text.replace('</<', ' / ')        # Corrige </< para /
        text = text.replace('<</', ' / ')        # Corrige <</ para /
        text = text.replace('</', ' /')          # Corrige </ para /
        
        # Remove caracteres especiais problemáticos em torno do UN (mais conservativo)  
        text = re.sub(r'<[/<]*\s*UN', ' UN ', text)
        
        # Corrige barras duplas que podem ter sido criadas
        text = re.sub(r'/\s*/\s*/', ' / ', text)
        
        # Normaliza espaçamento múltiplo mas preserva quebras de linha
        text = re.sub(r'[ \t]+', ' ', text)  # Só espaços e tabs, não quebras de linha
        
        logger.debug(f"Text normalized: {len(text)} chars")
        return text
    
    def _clean_extracted_text(self, text: str) -> str:
        """
        Limpa texto extraído de artefatos de PDF como cabeçalhos, rodapés e formatação.
        """
        lines = text.split('\n')
        cleaned_lines = []
        current_item = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Padrões para ignorar (cabeçalhos, metadados, formatação)
            # IMPORTANTE: Não remover linhas com dados essenciais (Orçamento Nº, Cliente, Vendedor, etc.)
            skip_patterns = [
                r'^PMCELL\s+São\s+Paulo',             # Cabeçalho da empresa
                r'^V\.\s+Zabin\s+Tecnologia',         # Nome da empresa
                r'^CNPJ:\s*\d+',                      # CNPJ
                r'^I\.E:\s*\d+',                      # Inscrição estadual
                r'^Rua\s+Comendador',                 # Endereço
                r'^Condição\s+de\s+Pagto',            # Condição de pagamento
                r'^Forma\s+de\s+Pagto',               # Forma de pagamento
                r'^Validade\s+do\s+Orçamento',        # Validade
                r'^Código\s+Produto\s+Unid',          # Cabeçalho da tabela
                r'^\s*\d+\s+dia\(s\)\s*$',           # Linha isolada com dias
                r'^\d{1,2}\s+dia\(s\)\s*$',          # Variação da linha de dias
                r'^\s*\d+\s*-\s*\d+\s+dia\(s\)',     # Padrão como "25 - 0 dia(s)"
                r'^Página\s+\d+\s*$',                 # Marcadores de página
                r'^Orçamento\s*N[ºo°]?:?\s*\d+',      # Linha de orçamento (conflita com extração)
                r'^Código:\s*\d+.*Data:',             # Linha com código e data
                r'^Cliente:\s*[\d\.].*Forma\s*de',     # Linha de cliente completa
                r'^Vendedor:.*Validade',              # Linha de vendedor completa
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Se a linha começa com código de 5 dígitos seguido de /, é início de item
            if re.match(r'^\d{5}\s*/', line):
                # Finaliza item anterior se existir
                if current_item and self._is_valid_item_line(current_item):
                    cleaned_lines.append(current_item)
                    logger.debug(f"Added completed item: {current_item[:50]}...")
                elif current_item:
                    logger.debug(f"Discarded invalid item: {current_item[:50]}...")
                current_item = line
                logger.debug(f"Started new item: {line[:50]}...")
            elif current_item:
                # Verifica se é continuação válida de item
                if (re.search(r'/\s*UN\s*/', line) or 
                    re.search(r'/\s*\d+\s*/\s*[\d,\.]+\s*/\s*[\d,\.]+', line)):
                    current_item += " " + line
                elif not re.match(r'^\d{5}', line):
                    # Verifica se não é um artefato antes de adicionar à descrição
                    # Não adicionar marcadores de página, cabeçalhos, etc.
                    artifact_patterns = [
                        r'^Página\s+\d+\s*$',                 # Marcadores de página
                        r'^PMCELL\s+São\s+Paulo',             # Cabeçalho da empresa
                        r'^V\.\s+Zabin\s+Tecnologia',         # Nome da empresa
                        r'^CNPJ:\s*\d+',                      # CNPJ
                        r'^I\.E:\s*\d+',                      # Inscrição estadual
                        r'^Rua\s+Comendador',                 # Endereço
                        r'^Código\s+Produto\s+Unid',          # Cabeçalho da tabela
                        r'^\s*\d+\s+dia\(s\)\s*$',           # Linha isolada com dias
                        r'^Orçamento\s*N[ºo°]?:?\s*\d+',      # Linha de orçamento
                        r'^Código:\s*\d+.*Data:',             # Linha com código e data
                        r'^Cliente:\s*[\d\.].*Forma\s*de',     # Linha de cliente completa
                        r'^Vendedor:.*Validade',              # Linha de vendedor completa
                    ]
                    
                    is_artifact = any(re.search(pattern, line, re.IGNORECASE) 
                                    for pattern in artifact_patterns)
                    
                    if not is_artifact:
                        # Possível continuação de item (descrição quebrada)
                        current_item += " " + line
                    else:
                        # É um artefato - finalizar item atual se válido
                        if self._is_valid_item_line(current_item):
                            cleaned_lines.append(current_item)
                            logger.debug(f"Added item before artifact: {current_item[:50]}...")
                        elif current_item:
                            logger.debug(f"Discarded invalid item before artifact: {current_item[:50]}...")
                        current_item = ""
            else:
                # Linha independente que pode ser item completo ou metadados
                if self._is_valid_item_line(line):
                    cleaned_lines.append(line)
                else:
                    # Preserva linhas importantes: metadados e informações de valores
                    important_patterns = [
                        r'Orçamento\s*N[ºo°]?:?\s*\d+',      # Número do orçamento
                        r'Cliente:\s*',                       # Cliente
                        r'Vendedor:\s*',                      # Vendedor 
                        r'Data:\s*\d{2}/\d{2}/\d{2}',        # Data
                        r'VALOR\s+TOTAL\s*R\$',              # Valor total
                        r'VALOR\s+A\s+PAGAR',                # Valor a pagar
                        r'DESCONTO\s*R\$',                   # Desconto
                    ]
                    
                    is_important = any(re.search(pattern, line, re.IGNORECASE) 
                                     for pattern in important_patterns)
                    
                    if is_important:
                        cleaned_lines.append(line)
        
        # Adiciona último item se válido
        if current_item and self._is_valid_item_line(current_item):
            cleaned_lines.append(current_item)
            logger.debug(f"Added final item: {current_item[:50]}...")
        elif current_item:
            logger.debug(f"Discarded final invalid item: {current_item[:50]}...")
        
        # Debug: Log quantos itens foram encontrados
        item_count = sum(1 for line in cleaned_lines if self._is_valid_item_line(line))
        logger.debug(f"Text cleaning found {item_count} valid item lines")
        
        return '\n'.join(cleaned_lines)
    
    def _is_valid_item_line(self, line: str) -> bool:
        """
        Verifica se uma linha representa um item válido.
        """
        if not line or not line.strip():
            return False
        
        # Deve ter estrutura básica de item: código + referência + UN + preços
        has_code = re.search(r'^\d{3,5}\s*/', line)
        has_unit = re.search(r'/\s*UN\s*/', line)
        has_prices = len(re.findall(r'[\d,\.]+', line)) >= 3  # quantidade + 2 preços mínimo
        
        # Não deve conter artefatos de cabeçalho
        has_artifacts = (
            'Código Produto Unid' in line or
            'Quant. Valor Total' in line or
            'dia(s)' in line or
            len(line.split()) < 4  # Muito poucos campos
        )
        
        return has_code and has_unit and has_prices and not has_artifacts
    
    def _is_suspicious_match(self, groups: tuple) -> bool:
        """
        Verifica se um match de regex é suspeito (provavelmente artefato).
        """
        if not groups or len(groups) < 3:
            return True
        
        code = groups[0].strip() if groups[0] else ""
        reference = groups[1].strip() if groups[1] else ""
        
        # Códigos suspeitos (muito curtos ou claramente inválidos)
        suspicious_codes = [
            "07",  # Código muito curto que veio de artefato
            "00",  # Código genérico
        ]
        
        # Códigos muito curtos (menos de 3 dígitos) são suspeitos
        if len(code) < 3 or code in suspicious_codes:
            return True
        
        # Referência contém artefatos de cabeçalho
        if reference and any(artifact in reference for artifact in [
            "Código Produto",
            "Unid. Quant.",
            "Valor Total",
            "dia(s)",
            "\n",  # Quebras de linha na referência são suspeitas
        ]):
            return True
        
        return False
    
    def _is_valid_item_data(self, code: str, reference: str, quantity: str, unit_price: str, total_price: str) -> bool:
        """
        Valida se os dados extraídos representam um item válido.
        """
        try:
            # Código deve ter 3-5 dígitos (flexível para testes e PDFs variados)
            if not re.match(r'^\d{3,5}$', code):
                return False
            
            # Referência não deve estar vazia e não deve conter artefatos
            if not reference or len(reference.strip()) < 2:
                return False
            
            # Quantidade deve ser numérica e maior que 0
            qty = int(quantity)
            if qty <= 0:
                return False
            
            # Preços devem ser válidos
            unit_val = self._parse_money_value(unit_price)
            total_val = self._parse_money_value(total_price)
            
            if unit_val is None or total_val is None:
                return False
            
            if unit_val <= 0 or total_val <= 0:
                return False
            
            return True
            
        except (ValueError, TypeError):
            return False
    
    def _extract_with_pattern(self, text: str, pattern_name: str) -> Optional[str]:
        """Extrai dados usando um pattern específico, com fallback."""
        # Tenta padrão principal primeiro
        pattern = self.PATTERNS.get(pattern_name)
        if pattern:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        # Se falhar, tenta padrões de fallback
        fallback_patterns = self.FALLBACK_PATTERNS.get(pattern_name, [])
        for fallback_pattern in fallback_patterns:
            match = re.search(fallback_pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                logger.debug(f"Used fallback pattern for {pattern_name}: {fallback_pattern}")
                return match.group(1).strip()
        
        return None
    
    def _extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extrai lista de itens do pedido com padrões melhorados."""
        items = []
        
        # Tenta padrão principal primeiro
        pattern = self.PATTERNS['items']
        items.extend(self._extract_items_with_pattern(text, pattern))
        
        # Se não encontrou itens suficientes, tenta fallbacks
        if len(items) == 0:
            fallback_patterns = self.FALLBACK_PATTERNS.get('items', [])
            for fallback_pattern in fallback_patterns:
                found_items = self._extract_items_with_pattern(text, fallback_pattern)
                if found_items:
                    logger.debug(f"Used fallback pattern for items: {fallback_pattern}")
                    items.extend(found_items)
                    break  # Para no primeiro padrão que funcionar
        
        # Remove duplicatas baseado no código do produto
        seen_codes = set()
        unique_items = []
        for item in items:
            if item['product_code'] not in seen_codes:
                unique_items.append(item)
                seen_codes.add(item['product_code'])
        
        return unique_items
    
    def _extract_items_with_pattern(self, text: str, pattern: str) -> List[Dict[str, Any]]:
        """Extrai itens usando um padrão específico."""
        items = []
        
        for match in re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE):
            try:
                # O padrão melhorado pode ter diferentes números de grupos
                groups = match.groups()
                
                # Validação adicional: ignorar matches suspeitos
                if self._is_suspicious_match(groups):
                    logger.debug(f"Skipping suspicious match: {groups}")
                    continue
                
                # Análise dos grupos baseada no padrão usado
                if len(groups) >= 7:  # Padrão universal com 7 grupos
                    product_code = groups[0].strip()
                    product_reference = groups[1].strip()
                    product_description = groups[2].strip() if groups[2] else ""
                    extra_field = groups[3].strip() if groups[3] else ""
                    quantity = groups[4].strip()
                    unit_price = groups[5].strip()
                    total_price = groups[6].strip()
                    
                    # Combina referência e descrição
                    if product_description:
                        combined_name = f"{product_reference} - {product_description}"
                        if extra_field:
                            combined_name += f" ({extra_field})"
                    else:
                        combined_name = product_reference
                        
                elif len(groups) >= 6:  # Padrão sem descrição separada (6-7 grupos)
                    product_code = groups[0].strip()
                    product_reference = groups[1].strip()
                    quantity = groups[2].strip()
                    unit_price = groups[3].strip()
                    total_price = groups[4].strip()
                    
                    combined_name = product_reference
                    
                elif len(groups) == 5:  # Padrão simples usado em testes
                    product_code = groups[0].strip()
                    product_reference = groups[1].strip()
                    # Para 5 grupos: código, ref, quantidade, preço_unit, preço_total
                    quantity = groups[2].strip()
                    unit_price = groups[3].strip()
                    total_price = groups[4].strip()
                    
                    combined_name = product_reference
                    
                else:
                    logger.warning(f"Unexpected number of groups in item pattern: {len(groups)}")
                    continue
                
                # Validação final do item construído
                if not self._is_valid_item_data(product_code, product_reference, quantity, unit_price, total_price):
                    logger.debug(f"Skipping invalid item: code={product_code}, ref={product_reference}")
                    continue
                
                item = {
                    'product_code': product_code,
                    'product_reference': product_reference,
                    'product_name': combined_name,
                    'quantity': int(quantity),
                    'unit_price': self._parse_money_value(unit_price),
                    'total_price': self._parse_money_value(total_price)
                }
                items.append(item)
                
            except (ValueError, IndexError) as e:
                logger.warning(f"Error parsing item from match {match.groups()}: {e}")
                continue
            
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