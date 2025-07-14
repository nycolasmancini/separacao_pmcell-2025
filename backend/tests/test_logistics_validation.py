#!/usr/bin/env python3
"""
Test logistics validation fix.

This test verifies that the logistics validation now accepts both
display values (like "Cliente na loja") and normalized values 
(like "cliente_na_loja").
"""
import pytest
from datetime import datetime
from app.schemas.pdf import (
    PDFUploadRequest, 
    OrderCreateFromPDF, 
    PDFExtractedData,
    normalize_logistics_type,
    normalize_package_type
)


class TestLogisticsValidation:
    """Test logistics type validation fix."""
    
    def test_normalize_logistics_type(self):
        """Test logistics type normalization function."""
        test_cases = [
            ("Cliente na loja", "cliente_na_loja"),
            ("cliente na loja", "cliente_na_loja"),
            ("CLIENTE NA LOJA", "cliente_na_loja"),
            ("cliente_na_loja", "cliente_na_loja"),
            ("Melhor Envio", "melhor_envio"),
            ("Lalamove", "lalamove"),
            ("Ônibus", "onibus"),
            ("Onibus", "onibus"),
        ]
        
        for input_val, expected in test_cases:
            result = normalize_logistics_type(input_val)
            assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_val}'"
    
    def test_normalize_package_type(self):
        """Test package type normalization function."""
        test_cases = [
            ("Caixa", "caixa"),
            ("CAIXA", "caixa"),
            ("Sacola", "sacola"),
            ("sacola", "sacola"),
        ]
        
        for input_val, expected in test_cases:
            result = normalize_package_type(input_val)
            assert result == expected, f"Expected '{expected}', got '{result}' for input '{input_val}'"
    
    def test_pdf_upload_request_with_display_values(self):
        """Test PDFUploadRequest accepts display values."""
        request = PDFUploadRequest(
            logistics_type="Cliente na loja",
            package_type="Caixa",
            observations="Teste"
        )
        
        assert request.logistics_type == "cliente_na_loja"
        assert request.package_type == "caixa"
    
    def test_pdf_upload_request_with_normalized_values(self):
        """Test PDFUploadRequest accepts normalized values."""
        request = PDFUploadRequest(
            logistics_type="cliente_na_loja",
            package_type="caixa",
            observations="Teste"
        )
        
        assert request.logistics_type == "cliente_na_loja"
        assert request.package_type == "caixa"
    
    def test_order_create_from_pdf_with_display_values(self):
        """Test OrderCreateFromPDF accepts display values."""
        pdf_data = PDFExtractedData(
            order_number="27729",
            client_name="EMANOEL GOMES DA SILVA",
            seller_name="NYCOLAS HENDRIGO MANCINI",
            order_date=datetime(2025, 7, 9),
            total_value=65.0,
            items=[
                {
                    "product_code": "02992",
                    "product_reference": "WALLO F21",
                    "product_name": "WALLO F21 - FONE DE OUVIDO WALLO",
                    "quantity": 10,
                    "unit_price": 6.5,
                    "total_price": 65.0
                }
            ]
        )
        
        order = OrderCreateFromPDF(
            pdf_data=pdf_data,
            logistics_type="Cliente na loja",
            package_type="Caixa",
            observations="Fazer com carinho"
        )
        
        assert order.logistics_type == "cliente_na_loja"
        assert order.package_type == "caixa"
    
    def test_invalid_logistics_type_still_fails(self):
        """Test that invalid logistics types still fail validation."""
        with pytest.raises(ValueError, match="Invalid logistics type"):
            PDFUploadRequest(
                logistics_type="Invalid Type",
                package_type="Caixa"
            )
    
    def test_invalid_package_type_still_fails(self):
        """Test that invalid package types still fail validation."""
        with pytest.raises(ValueError, match="Invalid package type"):
            PDFUploadRequest(
                logistics_type="Lalamove",
                package_type="Invalid Package"
            )