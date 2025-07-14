#!/usr/bin/env python3
"""
Debug detalhado do processo de limpeza para entender por que 00909 está sendo perdido
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber
import re

def debug_cleaning_step_by_step(pdf_path: str):
    """Debug passo a passo do processo de limpeza."""
    print("DEBUG DETALHADO DO PROCESSO DE LIMPEZA")
    print("="*60)
    
    # Extrair texto bruto
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                raw_text += page_text + "\n"
    
    # Encontrar linha com 00909
    raw_lines = raw_text.split('\n')
    line_00909 = None
    line_00909_index = -1
    
    for i, line in enumerate(raw_lines):
        if '00909' in line.strip():
            line_00909 = line.strip()
            line_00909_index = i
            print(f"📍 LINHA COM 00909 ENCONTRADA (linha {i}):")
            print(f"   '{line_00909}'")
            break
    
    if not line_00909:
        print("❌ Linha com 00909 não encontrada!")
        return
    
    # Simular processo de limpeza passo a passo
    parser = PDFParser()
    
    print(f"\n🔧 SIMULANDO PROCESSO DE LIMPEZA:")
    print("-" * 40)
    
    lines = raw_text.split('\n')
    cleaned_lines = []
    current_item = ""
    
    for line_num, line in enumerate(lines):
        original_line = line
        line = line.strip()
        
        if line_num == line_00909_index:
            print(f"\n🎯 PROCESSANDO LINHA {line_num} (00909):")
            print(f"   Original: '{original_line}'")
            print(f"   Stripped: '{line}'")
        
        if not line:
            if line_num == line_00909_index:
                print("   ❌ Linha vazia após strip - PULADA")
            continue
        
        # Testar padrões de skip
        skip_patterns = [
            r'^PMCELL\s+São\s+Paulo',
            r'^V\.\s+Zabin\s+Tecnologia',
            r'^CNPJ:\s*\d+',
            r'^I\.E:\s*\d+',
            r'^Rua\s+Comendador',
            r'^Condição\s+de\s+Pagto',
            r'^Forma\s+de\s+Pagto',
            r'^Validade\s+do\s+Orçamento',
            r'^Código\s+Produto\s+Unid',
            r'^\s*\d+\s+dia\(s\)\s*$',
            r'^\d{1,2}\s+dia\(s\)\s*$',
            r'^\s*\d+\s*-\s*\d+\s+dia\(s\)',
        ]
        
        should_skip = False
        matched_pattern = None
        for pattern in skip_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                should_skip = True
                matched_pattern = pattern
                break
        
        if line_num == line_00909_index:
            if should_skip:
                print(f"   ❌ SKIP - Matched pattern: {matched_pattern}")
            else:
                print(f"   ✅ NÃO SKIP - Continue processando")
        
        if should_skip:
            continue
        
        # Verificar se é início de item
        if re.match(r'^\d{5}\s*/', line):
            if line_num == line_00909_index:
                print(f"   🎯 É INÍCIO DE ITEM")
            
            # Finaliza item anterior se existir
            if current_item and parser._is_valid_item_line(current_item):
                cleaned_lines.append(current_item)
                if line_num == line_00909_index:
                    print(f"   📝 Item anterior adicionado: {current_item[:50]}...")
            current_item = line
            
            if line_num == line_00909_index:
                print(f"   📝 Iniciando novo item: {current_item}")
                
        elif current_item:
            if line_num == line_00909_index:
                print(f"   🔗 Continuação de item existente")
                print(f"      Current item: {current_item[:50]}...")
                print(f"      Adding line: {line}")
            
            # Verifica se é continuação válida de item
            if (re.search(r'/\s*UN\s*/', line) or 
                re.search(r'/\s*\d+\s*/\s*[\d,\.]+\s*/\s*[\d,\.]+', line)):
                current_item += " " + line
                if line_num == line_00909_index:
                    print(f"      ✅ ADICIONADO (padrão UN ou preços)")
                    print(f"      New current_item: {current_item}")
            elif not re.match(r'^\d{5}', line):
                # Possível continuação de item (descrição quebrada)
                current_item += " " + line
                if line_num == line_00909_index:
                    print(f"      ✅ ADICIONADO (continuação)")
                    print(f"      New current_item: {current_item}")
        else:
            if line_num == line_00909_index:
                print(f"   🔍 Linha independente")
            
            # Linha independente que pode ser item completo ou metadados
            if parser._is_valid_item_line(line):
                cleaned_lines.append(line)
                if line_num == line_00909_index:
                    print(f"   ✅ ADICIONADO como item válido")
            else:
                # Mantém metadados importantes
                cleaned_lines.append(line)
                if line_num == line_00909_index:
                    print(f"   ✅ ADICIONADO como metadado")
    
    # Adiciona último item se válido
    if current_item and parser._is_valid_item_line(current_item):
        cleaned_lines.append(current_item)
        print(f"\n📝 ÚLTIMO ITEM ADICIONADO: {current_item[:50]}...")
    
    # Verificar se 00909 está no resultado final
    final_text = '\n'.join(cleaned_lines)
    if '00909' in final_text:
        print(f"\n✅ 00909 ENCONTRADO NO TEXTO LIMPO!")
        # Encontrar linha
        for i, line in enumerate(cleaned_lines):
            if '00909' in line:
                print(f"   Linha {i}: {line}")
    else:
        print(f"\n❌ 00909 NÃO ENCONTRADO NO TEXTO LIMPO!")
    
    print("="*60)

def main():
    if len(sys.argv) != 2:
        print("Uso: python3 debug_cleaning_process.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    debug_cleaning_step_by_step(pdf_path)

if __name__ == "__main__":
    main()