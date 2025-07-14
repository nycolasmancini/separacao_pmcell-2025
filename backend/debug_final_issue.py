#!/usr/bin/env python3
"""
Script para debug do problema específico dos códigos 00909 e 00970
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber
import re

def debug_specific_codes(pdf_path: str):
    """Debug específico para os códigos problemáticos."""
    print("DEBUG ESPECÍFICO - CÓDIGOS 00909 e 00970")
    print("="*60)
    
    parser = PDFParser()
    
    # Extrair texto bruto
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    
    # Aplicar limpeza
    cleaned_text = parser._clean_extracted_text(raw_text)
    
    # Procurar especificamente pelos códigos problemáticos
    target_codes = ['00909', '00970']
    
    for code in target_codes:
        print(f"\n🔍 ANALISANDO CÓDIGO {code}:")
        print("-" * 30)
        
        # Procurar no texto bruto
        pattern = rf'{code}.*?/\s*UN\s*/.*'
        raw_matches = re.findall(pattern, raw_text, re.IGNORECASE | re.MULTILINE)
        print(f"   Ocorrências no texto bruto: {len(raw_matches)}")
        for i, match in enumerate(raw_matches, 1):
            print(f"      {i}. {match[:80]}...")
        
        # Procurar no texto limpo
        clean_matches = re.findall(pattern, cleaned_text, re.IGNORECASE | re.MULTILINE)
        print(f"   Ocorrências no texto limpo: {len(clean_matches)}")
        for i, match in enumerate(clean_matches, 1):
            print(f"      {i}. {match[:80]}...")
        
        # Testar extração individual de cada match
        for i, match in enumerate(clean_matches, 1):
            print(f"   Testando extração do match {i}:")
            items = parser._extract_items_from_line(match)
            if items:
                print(f"      ✅ Extraído: {items[0]['product_code']} - {items[0]['product_name']}")
            else:
                print(f"      ❌ Não extraído")
    
    # Agora vamos simular o processo completo de extração
    print(f"\n🔧 SIMULANDO PROCESSO COMPLETO:")
    print("-" * 40)
    
    # Extrair todos os itens usando o método interno
    all_items = parser._extract_items(cleaned_text)
    
    # Contar ocorrências dos códigos problemáticos
    for code in target_codes:
        count = sum(1 for item in all_items if item['product_code'] == code)
        print(f"   Código {code} encontrado {count} vez(es) na extração completa")
        
        # Mostrar todos os itens com esse código
        items_with_code = [item for item in all_items if item['product_code'] == code]
        for i, item in enumerate(items_with_code, 1):
            print(f"      {i}. {item['product_name']}")
    
    # Verificar resultado final oficial
    print(f"\n📊 VERIFICAÇÃO FINAL:")
    print("-" * 30)
    result = parser.extract(Path(pdf_path))
    final_items = result.get('items', [])
    
    for code in target_codes:
        final_count = sum(1 for item in final_items if item['product_code'] == code)
        print(f"   Código {code} no resultado final: {final_count} vez(es)")
    
    print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_final_issue.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    debug_specific_codes(pdf_path)

if __name__ == "__main__":
    main()