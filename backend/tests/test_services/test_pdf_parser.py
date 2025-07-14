"""
Testes para o serviço de parser de PDF.

Seguindo TDD - Tests First!
"""
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from app.services.pdf_parser import PDFParser, PDFParseError


class TestPDFParser:
    """Testes para o parser de PDF."""
    
    @pytest.fixture
    def parser(self):
        """Fixture para criar instância do parser."""
        return PDFParser()
    
    @pytest.fixture
    def sample_pdf_path(self):
        """Caminho para PDF de exemplo."""
        return Path(__file__).parent.parent / "fixtures" / "pdfs" / "sample_order.pdf"
    
    def test_parser_instance_creation(self, parser):
        """Testa criação da instância do parser."""
        assert parser is not None
        assert hasattr(parser, 'extract')
        assert hasattr(parser, 'validate')
    
    def test_extract_order_number(self, parser, sample_pdf_path):
        """Testa extração do número do orçamento."""
        result = parser.extract(sample_pdf_path)
        assert 'order_number' in result
        assert result['order_number'] is not None
        assert result['order_number'].isdigit()
    
    def test_extract_client_name(self, parser, sample_pdf_path):
        """Testa extração do nome do cliente."""
        result = parser.extract(sample_pdf_path)
        assert 'client_name' in result
        assert result['client_name'] is not None
        assert len(result['client_name']) > 0
    
    def test_extract_seller_name(self, parser, sample_pdf_path):
        """Testa extração do nome do vendedor."""
        result = parser.extract(sample_pdf_path)
        assert 'seller_name' in result
        assert result['seller_name'] is not None
        assert len(result['seller_name']) > 0
    
    def test_extract_order_date(self, parser, sample_pdf_path):
        """Testa extração da data do pedido."""
        result = parser.extract(sample_pdf_path)
        assert 'order_date' in result
        assert result['order_date'] is not None
        assert isinstance(result['order_date'], datetime)
    
    def test_extract_total_value(self, parser, sample_pdf_path):
        """Testa extração do valor total."""
        result = parser.extract(sample_pdf_path)
        assert 'total_value' in result
        assert result['total_value'] is not None
        assert isinstance(result['total_value'], float)
        assert result['total_value'] > 0
    
    def test_extract_items(self, parser, sample_pdf_path):
        """Testa extração dos itens do pedido."""
        result = parser.extract(sample_pdf_path)
        assert 'items' in result
        assert isinstance(result['items'], list)
        assert len(result['items']) > 0
        
        # Verifica estrutura do primeiro item
        first_item = result['items'][0]
        required_fields = [
            'product_code', 'product_reference', 'product_name',
            'quantity', 'unit_price', 'total_price'
        ]
        for field in required_fields:
            assert field in first_item
    
    def test_validate_extracted_data(self, parser):
        """Testa validação dos dados extraídos."""
        valid_data = {
            'order_number': '12345',
            'client_name': 'Cliente Teste',
            'seller_name': 'Vendedor Teste',
            'order_date': datetime.now(),
            'total_value': 1500.50,
            'items': [
                {
                    'product_code': '001',
                    'product_reference': 'REF001',
                    'product_name': 'Produto Teste',
                    'quantity': 2,
                    'unit_price': 750.25,
                    'total_price': 1500.50
                }
            ]
        }
        assert parser.validate(valid_data) is True
    
    def test_validate_missing_required_field(self, parser):
        """Testa validação com campo obrigatório faltando."""
        invalid_data = {
            'order_number': '12345',
            # client_name faltando
            'seller_name': 'Vendedor Teste',
            'order_date': datetime.now(),
            'total_value': 1500.50,
            'items': []
        }
        with pytest.raises(PDFParseError, match="client_name"):
            parser.validate(invalid_data)
    
    def test_validate_empty_items(self, parser):
        """Testa validação com lista de itens vazia."""
        data_with_empty_items = {
            'order_number': '12345',
            'client_name': 'Cliente Teste',
            'seller_name': 'Vendedor Teste',
            'order_date': datetime.now(),
            'total_value': 1500.50,
            'items': []
        }
        with pytest.raises(PDFParseError, match="at least one item"):
            parser.validate(data_with_empty_items)
    
    def test_parse_value_with_brazilian_format(self, parser):
        """Testa parsing de valores monetários no formato brasileiro."""
        assert parser._parse_money_value("1.234,56") == 1234.56
        assert parser._parse_money_value("R$ 1.234,56") == 1234.56
        assert parser._parse_money_value("1234,56") == 1234.56
        assert parser._parse_money_value("1234.56") == 1234.56
        assert parser._parse_money_value("1.234.567") == 1234567.0
    
    def test_parse_date_brazilian_format(self, parser):
        """Testa parsing de datas no formato brasileiro."""
        date = parser._parse_date("12/07/24")
        assert date.day == 12
        assert date.month == 7
        assert date.year == 2024
        
        date2 = parser._parse_date("01/01/25")
        assert date2.year == 2025
    
    def test_extract_with_special_characters(self, parser):
        """Testa extração com caracteres especiais no PDF."""
        special_pdf_path = Path(__file__).parent.parent / "fixtures" / "pdfs" / "special_chars.pdf"
        result = parser.extract(special_pdf_path)
        # Deve processar sem erros mesmo com acentos e caracteres especiais
        assert result is not None
    
    def test_extract_multipage_pdf(self, parser):
        """Testa extração de PDF com múltiplas páginas."""
        multipage_pdf_path = Path(__file__).parent.parent / "fixtures" / "pdfs" / "multipage.pdf"
        result = parser.extract(multipage_pdf_path)
        # Deve extrair itens de todas as páginas
        assert len(result['items']) > 10  # assumindo que tem muitos itens
    
    def test_invalid_pdf_file(self, parser):
        """Testa comportamento com arquivo não-PDF."""
        invalid_path = Path(__file__).parent.parent / "fixtures" / "pdfs" / "not_a_pdf.txt"
        with pytest.raises(PDFParseError, match="Invalid PDF"):
            parser.extract(invalid_path)
    
    def test_corrupted_pdf(self, parser):
        """Testa comportamento com PDF corrompido."""
        corrupted_path = Path(__file__).parent.parent / "fixtures" / "pdfs" / "corrupted.pdf"
        with pytest.raises(PDFParseError):
            parser.extract(corrupted_path)
    
    def test_pdf_without_required_fields(self, parser):
        """Testa PDF que não contém os campos obrigatórios."""
        incomplete_pdf_path = Path(__file__).parent.parent / "fixtures" / "pdfs" / "incomplete.pdf"
        with pytest.raises(PDFParseError, match="Missing required field"):
            parser.extract(incomplete_pdf_path)
    
    def test_item_total_calculation(self, parser):
        """Testa se o total do item é calculado corretamente."""
        item_data = parser._parse_item_line(
            "001 / REF001 --> Produto Teste / UN / 5 / 100,00 / 500,00"
        )
        assert item_data['quantity'] == 5
        assert item_data['unit_price'] == 100.00
        assert item_data['total_price'] == 500.00
    
    def test_clean_text_fields(self, parser):
        """Testa limpeza de campos de texto."""
        assert parser._clean_text("  Cliente Teste  \n") == "Cliente Teste"
        assert parser._clean_text("VENDEDOR: João") == "João"
        assert parser._clean_text("Cliente: Maria   Forma") == "Maria"


class TestPDFParserPatterns:
    """Testes específicos para os patterns regex."""
    
    @pytest.fixture
    def parser(self):
        return PDFParser()
    
    def test_order_number_pattern(self, parser):
        """Testa pattern de número do orçamento."""
        text = "Orçamento Nº: 12345\nOutras informações"
        match = parser._extract_with_pattern(text, 'order_number')
        assert match == "12345"
    
    def test_client_pattern(self, parser):
        """Testa pattern de cliente."""
        text = "Cliente: EMPRESA TESTE LTDA\nForma de Pagamento"
        match = parser._extract_with_pattern(text, 'client')
        assert match == "EMPRESA TESTE LTDA"
    
    def test_seller_pattern(self, parser):
        """Testa pattern de vendedor."""
        text = "Vendedor: João Silva\nValidade: 30 dias"
        match = parser._extract_with_pattern(text, 'seller')
        assert match == "João Silva"
    
    def test_total_value_pattern(self, parser):
        """Testa pattern de valor total."""
        text = "VALOR A PAGAR R$ 1.234,56"
        match = parser._extract_with_pattern(text, 'total_value')
        assert match == "1.234,56"
    
    def test_items_pattern(self, parser):
        """Testa pattern de itens."""
        line = "001 / REF-123 --> PRODUTO TESTE / UN / 10 / 50,00 / 500,00"
        items = parser._extract_items_from_line(line)
        assert len(items) == 1
        assert items[0]['product_code'] == "001"
        assert items[0]['product_reference'] == "REF-123"
        assert items[0]['product_name'] == "REF-123 - PRODUTO TESTE"
        assert items[0]['quantity'] == 10
        assert items[0]['unit_price'] == 50.00
        assert items[0]['total_price'] == 500.00


class TestPDFParserIntegration:
    """Testes de integração com PDFs reais."""
    
    @pytest.fixture
    def parser(self):
        return PDFParser()
    
    @pytest.mark.parametrize("pdf_name,expected_order_number", [
        ("Teste 2.pdf", "27772"),
        ("Teste 3.pdf", "27771"), 
        ("Teste 4.pdf", "27769"),
        ("Teste 5.pdf", "27766"),
        ("Teste 6.pdf", "27742"),
    ])
    def test_real_pdfs_extraction(self, parser, pdf_name, expected_order_number):
        """Testa extração com os PDFs reais fornecidos."""
        pdf_path = Path("/Users/nycolasmancini/Downloads") / pdf_name
        if pdf_path.exists():
            result = parser.extract(pdf_path)
            assert result['order_number'] == expected_order_number
            assert result['client_name'] is not None
            assert result['seller_name'] is not None
            assert result['total_value'] > 0
            assert len(result['items']) > 0