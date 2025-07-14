#!/usr/bin/env python3
"""
Script para identificar quais itens não estão sendo extraídos no Teste 5.pdf
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber
import re

def analyze_missing_items(pdf_path: str):
    """Analisa quais itens estão sendo perdidos na extração."""
    print("ANÁLISE DE ITENS PERDIDOS - TESTE 5")
    print("="*60)
    
    # Extrair texto bruto
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    
    # Criar parser
    parser = PDFParser()
    
    # Aplicar limpeza
    cleaned_text = parser._clean_extracted_text(raw_text)
    
    # Encontrar todas as linhas que parecem itens
    lines = cleaned_text.split('\n')
    potential_items = []
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Procurar linhas que começam com código de item
        if re.match(r'^\d{4,5}\s*/', line):
            potential_items.append((i, line))
    
    print(f"📊 ITENS POTENCIAIS ENCONTRADOS: {len(potential_items)}")
    print("-" * 60)
    
    # Testar cada item individual
    valid_items = []
    filtered_items = []
    
    for line_num, line in potential_items:
        # Testar se a linha é válida
        is_valid_line = parser._is_valid_item_line(line)
        
        # Testar extração individual
        extracted_items = parser._extract_items_from_line(line)
        
        if extracted_items:
            valid_items.append((line_num, line, extracted_items[0]))
            print(f"✅ Linha {line_num:2d}: {extracted_items[0]['product_code']} - EXTRAÍDO")
        else:
            filtered_items.append((line_num, line, is_valid_line))
            print(f"❌ Linha {line_num:2d}: FILTRADO - Válida: {is_valid_line}")
            print(f"    {line[:80]}...")
            
            # Testar pattern matching manual
            pattern = parser.PATTERNS['items']
            matches = re.findall(pattern, line, re.IGNORECASE)
            if matches:
                print(f"    🔍 Pattern match: {matches[0][:3]}...")
                # Testar validação manual
                groups = matches[0]
                if len(groups) >= 7:
                    code = groups[0].strip()
                    ref = groups[1].strip()
                    qty = groups[4].strip()
                    unit_price = groups[5].strip()
                    total_price = groups[6].strip()
                    
                    is_suspicious = parser._is_suspicious_match(groups)
                    is_valid_data = parser._is_valid_item_data(code, ref, qty, unit_price, total_price)
                    
                    print(f"    🔍 Suspicious: {is_suspicious}, Valid data: {is_valid_data}")
                    print(f"    🔍 Code: '{code}', Ref: '{ref[:20]}...'")
            print()
    
    print("="*60)
    print(f"📈 RESUMO:")
    print(f"   Total potencial: {len(potential_items)}")
    print(f"   Extraídos: {len(valid_items)}")
    print(f"   Filtrados: {len(filtered_items)}")
    
    if filtered_items:
        print(f"\n📋 ITENS FILTRADOS DETALHADOS:")
        for line_num, line, is_valid_line in filtered_items:
            print(f"   Linha {line_num}: {line}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_missing_items.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    analyze_missing_items(pdf_path)

if __name__ == "__main__":
    main()