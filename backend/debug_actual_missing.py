#!/usr/bin/env python3
"""
Script para encontrar exatamente qual item está faltando no Teste 5.pdf
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber

def find_actual_missing_item(pdf_path: str):
    """Encontra o item específico que está faltando."""
    print("PROCURANDO ITEM FALTANTE NO TESTE 5")
    print("="*60)
    
    # Extrair resultado oficial
    parser = PDFParser()
    result = parser.extract(Path(pdf_path))
    extracted_codes = set([item['product_code'] for item in result['items']])
    
    print(f"📊 CÓDIGOS EXTRAÍDOS PELO PARSER: {len(extracted_codes)}")
    
    # Extrair texto bruto e procurar por TODOS os padrões de item
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    
    # Procurar todos os códigos que aparecem no formato de item no texto bruto
    import re
    
    # Padrão simples para encontrar linhas que parecem itens
    pattern = r'(\d{4,5})\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*.*?/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    
    raw_matches = re.findall(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
    raw_codes = set([match[0] for match in raw_matches])
    
    print(f"📊 CÓDIGOS ENCONTRADOS NO TEXTO BRUTO: {len(raw_codes)}")
    
    # Encontrar a diferença
    missing_codes = raw_codes - extracted_codes
    extra_codes = extracted_codes - raw_codes
    
    print(f"\n🔍 ANÁLISE:")
    print(f"   Códigos no texto bruto: {len(raw_codes)}")
    print(f"   Códigos extraídos: {len(extracted_codes)}")
    print(f"   Códigos em falta: {len(missing_codes)}")
    print(f"   Códigos extras: {len(extra_codes)}")
    
    if missing_codes:
        print(f"\n❌ CÓDIGOS FALTANDO NA EXTRAÇÃO:")
        for code in sorted(missing_codes):
            # Encontrar o item completo no texto
            item_pattern = rf'{code}\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*.*?/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
            item_match = re.search(item_pattern, raw_text, re.IGNORECASE | re.MULTILINE)
            if item_match:
                full_match = item_match.group(0)
                print(f"   {code}: {full_match[:80]}...")
                
                # Testar por que não foi extraído
                print(f"      🔍 Testando extração individual...")
                test_items = parser._extract_items_from_line(full_match)
                if test_items:
                    print(f"      ✅ Extraído individualmente: {test_items[0]['product_code']}")
                else:
                    print(f"      ❌ Não extraído nem individualmente")
                    
                    # Testar validações
                    groups = item_match.groups()
                    full_groups = (code,) + groups
                    
                    is_suspicious = parser._is_suspicious_match(full_groups)
                    print(f"      🔍 Is suspicious: {is_suspicious}")
                    
                    if len(full_groups) >= 5:
                        ref = groups[0] if groups[0] else ""
                        qty = groups[2] if len(groups) > 2 else ""
                        unit_price = groups[3] if len(groups) > 3 else ""
                        total_price = groups[4] if len(groups) > 4 else ""
                        
                        is_valid = parser._is_valid_item_data(code, ref, qty, unit_price, total_price)
                        print(f"      🔍 Is valid data: {is_valid}")
                        
                        if not is_valid:
                            print(f"      🔍 Dados: code='{code}', ref='{ref}', qty='{qty}', unit='{unit_price}', total='{total_price}'")
    
    if extra_codes:
        print(f"\n ℹ️ CÓDIGOS EXTRAS NA EXTRAÇÃO:")
        for code in sorted(extra_codes):
            print(f"   {code}")
    
    # Listar todos os códigos para referência
    print(f"\n📋 TODOS OS CÓDIGOS DO TEXTO BRUTO:")
    for i, code in enumerate(sorted(raw_codes), 1):
        status = "✅" if code in extracted_codes else "❌"
        print(f"   {i:2d}. {status} {code}")
    
    print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_actual_missing.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    find_actual_missing_item(pdf_path)

if __name__ == "__main__":
    main()