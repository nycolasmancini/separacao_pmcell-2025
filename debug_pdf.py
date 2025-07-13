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

if __name__ == "__main__":
    # Path do PDF
    pdf_path = "/Users/nycolasmancini/Documents/Orcamento - 27830 - Lukad - R$ 1810,00.pdf"
    
    if not Path(pdf_path).exists():
        print(f"❌ ERRO: Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    analyze_pdf(pdf_path)