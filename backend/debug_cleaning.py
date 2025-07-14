#!/usr/bin/env python3
"""
Debug script to see what's happening with text cleaning.
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber

def debug_text_cleaning(pdf_path: str):
    """Debug the text cleaning process."""
    print("DEBUG: PROCESSO DE LIMPEZA DE TEXTO")
    print("="*50)
    
    # Get raw text
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    
    print("1. TEXTO BRUTO (primeiras 20 linhas):")
    print("-" * 30)
    raw_lines = raw_text.split('\n')[:20]
    for i, line in enumerate(raw_lines, 1):
        print(f"{i:2d}: {line}")
    
    # Apply cleaning
    parser = PDFParser()
    cleaned_text = parser._clean_extracted_text(raw_text)
    
    print(f"\n2. TEXTO LIMPO (todas as linhas):")
    print("-" * 30)
    cleaned_lines = cleaned_text.split('\n')
    for i, line in enumerate(cleaned_lines, 1):
        print(f"{i:2d}: {line}")
    
    # Test pattern extraction on cleaned text
    print(f"\n3. TESTE DE EXTRAÇÃO DE PADRÕES:")
    print("-" * 30)
    
    # Test order number pattern
    order_pattern = r'Orçamento\s*N[ºo°]?:?\s*(\d+)'
    import re
    
    print("Buscando número do orçamento...")
    match = re.search(order_pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
    if match:
        print(f"✅ Número encontrado: {match.group(1)}")
    else:
        print("❌ Número não encontrado")
        
        # Try in raw text
        match_raw = re.search(order_pattern, raw_text, re.IGNORECASE | re.MULTILINE)
        if match_raw:
            print(f"🔍 Número estava no texto bruto: {match_raw.group(1)}")
        else:
            print("🔍 Número não está nem no texto bruto")
    
    # Test other patterns
    patterns = {
        'client': r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
        'seller': r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
        'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
        'total_value': r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
    }
    
    for name, pattern in patterns.items():
        match = re.search(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
        if match:
            print(f"✅ {name}: {match.group(1)}")
        else:
            print(f"❌ {name}: não encontrado")

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_cleaning.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    debug_text_cleaning(pdf_path)

if __name__ == "__main__":
    main()