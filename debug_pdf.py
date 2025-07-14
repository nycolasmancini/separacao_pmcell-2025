#!/usr/bin/env python3
"""
Debug script para analisar PDF da PMCELL e identificar problemas de extração.
"""
import re
import sys
from pathlib import Path
import pdfplumber
import PyPDF2

# Patterns do sistema atual
PATTERNS = {
    'order_number': r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
    'client': r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
    'seller': r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
    'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
    'total_value': r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
    'items': r'(\d+)\s*/\s*([^>]+?)\s*-->\s*([^/]+)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
}

def extract_text_pdfplumber(pdf_path):
    """Extrai texto usando pdfplumber."""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if page_text:
                    print(f"\n=== PÁGINA {page_num + 1} (pdfplumber) ===")
                    print(page_text)
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Erro com pdfplumber: {e}")
        return ""

def extract_text_pypdf2(pdf_path):
    """Extrai texto usando PyPDF2."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    print(f"\n=== PÁGINA {page_num + 1} (PyPDF2) ===")
                    print(page_text)
                    text += page_text + "\n"
            return text
    except Exception as e:
        print(f"Erro com PyPDF2: {e}")
        return ""

def test_patterns(text):
    """Testa todos os patterns no texto extraído."""
    print("\n" + "="*80)
    print("TESTANDO PATTERNS")
    print("="*80)
    
    for pattern_name, pattern in PATTERNS.items():
        print(f"\n--- Pattern: {pattern_name} ---")
        print(f"Regex: {pattern}")
        
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            print(f"✅ ENCONTRADO: {match.group(1)}")
            if len(match.groups()) > 1:
                print(f"   Grupos: {match.groups()}")
        else:
            print("❌ NÃO ENCONTRADO")
            
            # Busca por partes do pattern para debug
            if pattern_name == 'order_number':
                # Testa variações
                test_patterns = [
                    r'Orçamento',
                    r'N[ºo°]',
                    r'\d+',
                    r'Orçamento.*\d+',
                    r'(\d+)'
                ]
                for test_pattern in test_patterns:
                    test_match = re.search(test_pattern, text, re.IGNORECASE)
                    if test_match:
                        print(f"   Encontrado parte: '{test_pattern}' -> {test_match.group(0)}")

def analyze_pdf(pdf_path):
    """Análise completa do PDF."""
    print(f"Analisando PDF: {pdf_path}")
    print("="*80)
    
    # Teste com pdfplumber
    print("\n🔍 EXTRAINDO COM PDFPLUMBER...")
    text_pdfplumber = extract_text_pdfplumber(pdf_path)
    
    # Teste com PyPDF2  
    print("\n🔍 EXTRAINDO COM PYPDF2...")
    text_pypdf2 = extract_text_pypdf2(pdf_path)
    
    # Escolhe o melhor texto
    text = text_pdfplumber if text_pdfplumber.strip() else text_pypdf2
    
    if not text.strip():
        print("❌ ERRO: Não foi possível extrair nenhum texto do PDF!")
        return
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Texto extraído: {len(text)} caracteres")
    print(f"   Linhas: {len(text.splitlines())}")
    
    # Testa patterns
    test_patterns(text)
    
    # Busca por palavras-chave
    print("\n" + "="*80)
    print("BUSCA POR PALAVRAS-CHAVE")
    print("="*80)
    
    keywords = ['orçamento', 'cliente', 'vendedor', 'data', 'valor', 'pagar', 'lukad']
    for keyword in keywords:
        if keyword.lower() in text.lower():
            print(f"✅ Encontrado: '{keyword}'")
            # Mostra context
            lines = text.lower().splitlines()
            for i, line in enumerate(lines):
                if keyword in line:
                    print(f"   Linha {i+1}: {line.strip()}")
        else:
            print(f"❌ Não encontrado: '{keyword}'")
    
    # Analisa as linhas de itens especificamente
    print("\n" + "="*80)
    print("ANÁLISE DAS LINHAS DE ITENS")
    print("="*80)
    
    lines = text.splitlines()
    item_lines = []
    for i, line in enumerate(lines):
        if '-->' in line and 'UN' in line:
            print(f"Linha {i+1}: {line.strip()}")
            item_lines.append(line.strip())
    
    print(f"\nTotal de linhas com itens encontradas: {len(item_lines)}")
    
    # Testa novo pattern para itens
    print("\n--- TESTANDO NOVO PATTERN PARA ITENS ---")
    new_item_pattern = r'(\d{5})\s+([A-Z0-9\s]+)\s+-->\s+([^U]+)\s+UN\s+(\d+)\s+([\d,\.]+)\s+([\d,\.]+)'
    
    for line in item_lines:
        match = re.search(new_item_pattern, line)
        if match:
            print(f"✅ MATCH: {match.groups()}")
        else:
            print(f"❌ NO MATCH: {line}")
            
    # Testa pattern mais flexível
    print("\n--- TESTANDO PATTERN MAIS FLEXÍVEL ---")
    flexible_pattern = r'(\d+)\s+([A-Z0-9\s\-]+)\s+-->\s+([^U]+)\s+UN\s+(\d+)\s+([\d,\.]+)\s+([\d,\.]+)'
    
    for line in item_lines:
        match = re.search(flexible_pattern, line)
        if match:
            print(f"✅ MATCH: {match.groups()}")
        else:
            print(f"❌ NO MATCH: {line}")
    
    # Testa pattern correto baseado na análise
    print("\n--- TESTANDO PATTERN CORRETO ---")
    correct_pattern = r'(\d+)\s+([A-Z0-9\s\-]+?)\s+-->\s+([^U]+?)\s+UN\s+(\d+)\s+([\d,\.]+)\s+([\d,\.]+)'
    
    for line in item_lines:
        match = re.search(correct_pattern, line)
        if match:
            print(f"✅ MATCH: {match.groups()}")
        else:
            print(f"❌ NO MATCH: {line}")
    
    # Analisa formato exato - sem espaços entre grupos
    print("\n--- ANÁLISE FORMATO EXATO ---")
    for i, line in enumerate(item_lines):
        print(f"Linha {i+1}: '{line}'")
        # Quebra a linha em componentes
        parts = line.split()
        print(f"  Partes: {parts}")
        
        # Encontra o índice do '-->'
        if '-->' in parts:
            arrow_idx = parts.index('-->')
            print(f"  Seta em índice: {arrow_idx}")
            
            # Encontra o índice do 'UN'
            if 'UN' in parts:
                un_idx = parts.index('UN')
                print(f"  UN em índice: {un_idx}")
                
                # Reconstrói os componentes
                codigo = parts[0]
                modelo = ' '.join(parts[1:arrow_idx])
                descricao = ' '.join(parts[arrow_idx+1:un_idx])
                quantidade = parts[un_idx+1]
                valor_unit = parts[un_idx+2]
                valor_total = parts[un_idx+3]
                
                print(f"  Código: '{codigo}'")
                print(f"  Modelo: '{modelo}'")
                print(f"  Descrição: '{descricao}'")
                print(f"  Quantidade: '{quantidade}'")
                print(f"  Valor Unitário: '{valor_unit}'")
                print(f"  Valor Total: '{valor_total}'")
        print()
    
    # Testa pattern baseado na análise
    print("\n--- TESTANDO PATTERN BASEADO NA ANÁLISE ---")
    analysis_pattern = r'(\d+)\s+([A-Z0-9\s\-]+?)\s+-->\s+(.+?)\s+UN\s+(\d+)\s+([\d,\.]+)\s+([\d,\.]+)'
    
    matches = []
    for line in item_lines:
        match = re.search(analysis_pattern, line)
        if match:
            matches.append(match.groups())
            print(f"✅ MATCH: {match.groups()}")
        else:
            print(f"❌ NO MATCH: {line}")
    
    print(f"\nTotal de matches: {len(matches)}/{len(item_lines)}")

if __name__ == "__main__":
    # Path do PDF
    pdf_path = "/Users/nycolasmancini/Documents/Orcamento - 27729 - Cassia - R$ 944,00.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ ERRO: Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    analyze_pdf(pdf_path)