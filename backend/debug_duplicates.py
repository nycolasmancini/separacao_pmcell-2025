#!/usr/bin/env python3
"""
Script para identificar duplicatas sendo removidas no Teste 5.pdf
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber
from collections import Counter

def analyze_duplicates(pdf_path: str):
    """Analisa duplicatas sendo removidas."""
    print("ANÁLISE DE DUPLICATAS - TESTE 5")
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
    
    # Extrair todos os itens sem remoção de duplicatas
    items_before_dedup = []
    
    # Testar padrão principal
    pattern = parser.PATTERNS['items']
    import re
    
    for match in re.finditer(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE):
        try:
            groups = match.groups()
            
            # Validação
            if parser._is_suspicious_match(groups):
                continue
                
            if len(groups) >= 7:
                product_code = groups[0].strip()
                product_reference = groups[1].strip()
                product_description = groups[2].strip() if groups[2] else ""
                extra_field = groups[3].strip() if groups[3] else ""
                quantity = groups[4].strip()
                unit_price = groups[5].strip()
                total_price = groups[6].strip()
                
                if product_description:
                    combined_name = f"{product_reference} - {product_description}"
                    if extra_field:
                        combined_name += f" ({extra_field})"
                else:
                    combined_name = product_reference
                    
                # Validação final
                if not parser._is_valid_item_data(product_code, product_reference, quantity, unit_price, total_price):
                    continue
                
                item = {
                    'product_code': product_code,
                    'product_reference': product_reference,
                    'product_name': combined_name,
                    'quantity': int(quantity),
                    'unit_price': parser._parse_money_value(unit_price),
                    'total_price': parser._parse_money_value(total_price)
                }
                items_before_dedup.append(item)
                
        except Exception as e:
            continue
    
    print(f"📊 ITENS ANTES DA REMOÇÃO DE DUPLICATAS: {len(items_before_dedup)}")
    
    # Contar códigos
    codes_count = Counter([item['product_code'] for item in items_before_dedup])
    duplicates = {code: count for code, count in codes_count.items() if count > 1}
    
    if duplicates:
        print(f"🔍 CÓDIGOS DUPLICADOS ENCONTRADOS:")
        for code, count in duplicates.items():
            print(f"   {code}: {count} ocorrências")
            
            # Mostrar os itens duplicados
            duplicate_items = [item for item in items_before_dedup if item['product_code'] == code]
            for i, item in enumerate(duplicate_items):
                print(f"      {i+1}. {item['product_name']}")
        print()
    else:
        print("✅ Nenhuma duplicata encontrada!")
    
    # Agora extrair com o método oficial do parser para comparar
    official_result = parser.extract(Path(pdf_path))
    official_items = official_result.get('items', [])
    
    print(f"📊 ITENS NO RESULTADO OFICIAL: {len(official_items)}")
    
    # Comparar códigos
    codes_before = set([item['product_code'] for item in items_before_dedup])
    codes_after = set([item['product_code'] for item in official_items])
    
    missing_codes = codes_before - codes_after
    if missing_codes:
        print(f"❌ CÓDIGOS PERDIDOS: {missing_codes}")
        for code in missing_codes:
            lost_items = [item for item in items_before_dedup if item['product_code'] == code]
            for item in lost_items:
                print(f"   {code}: {item['product_name']}")
    else:
        print("✅ Nenhum código perdido!")
    
    extra_codes = codes_after - codes_before
    if extra_codes:
        print(f"ℹ️  CÓDIGOS EXTRAS: {extra_codes}")
    
    print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_duplicates.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    analyze_duplicates(pdf_path)

if __name__ == "__main__":
    main()