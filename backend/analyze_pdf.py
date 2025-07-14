#!/usr/bin/env python3
"""
Script para análise detalhada de PDFs para melhorar os patterns de extração.
"""

import sys
import pdfplumber
import PyPDF2
import re
from pathlib import Path

def analyze_pdf_with_pdfplumber(pdf_path):
    """Analisa PDF usando pdfplumber"""
    print("="*60)
    print("ANÁLISE COM PDFPLUMBER")
    print("="*60)
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"Número de páginas: {len(pdf.pages)}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\n--- PÁGINA {page_num} ---")
                
                # Extrair texto
                text = page.extract_text()
                if text:
                    print("TEXTO EXTRAÍDO:")
                    print(text)
                    print("\nTEXTO COM CARACTERES ESPECIAIS VISÍVEIS:")
                    print(repr(text))
                
                # Extrair tabelas se houver
                tables = page.extract_tables()
                if tables:
                    print(f"\nTABELAS ENCONTRADAS: {len(tables)}")
                    for i, table in enumerate(tables):
                        print(f"Tabela {i+1}:")
                        for row in table:
                            print(row)
                        print()
                
    except Exception as e:
        print(f"Erro com pdfplumber: {e}")

def analyze_pdf_with_pypdf2(pdf_path):
    """Analisa PDF usando PyPDF2"""
    print("\n" + "="*60)
    print("ANÁLISE COM PyPDF2")
    print("="*60)
    
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            print(f"Número de páginas: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                print(f"\n--- PÁGINA {page_num} ---")
                
                text = page.extract_text()
                if text:
                    print("TEXTO EXTRAÍDO:")
                    print(text)
                    print("\nTEXTO COM CARACTERES ESPECIAIS VISÍVEIS:")
                    print(repr(text))
                
    except Exception as e:
        print(f"Erro com PyPDF2: {e}")

def analyze_patterns(text):
    """Analisa o texto extraído procurando por padrões conhecidos"""
    print("\n" + "="*60)
    print("ANÁLISE DE PADRÕES")
    print("="*60)
    
    # Padrões atuais do sistema
    current_patterns = {
        'order_number': r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
        'client': r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
        'seller': r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
        'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
        'total_value': r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
        'items': r'(\d+)\s*[\/\s]+([A-Z0-9\s\-]+?)\s*-->\s*(.+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)'
    }
    
    # Novos padrões mais flexíveis
    flexible_patterns = {
        'order_number': [
            r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
            r'Or[çc]amento\s*[-\s]*(\d+)',
            r'N[ºo°]?\s*(\d+)',
        ],
        'client': [
            r'Cliente:\s*([^\n]+?)(?:\s*Forma|$)',
            r'Cliente\s*[-:]\s*([^\n]+?)(?:\s*Forma|$)',
            r'Cliente\s*([^\n]+?)(?:\s*Forma|$)',
        ],
        'seller': [
            r'Vendedor:\s*([^\n]+?)(?:\s*Validade|$)',
            r'Vendedor\s*[-:]\s*([^\n]+?)(?:\s*Validade|$)',
            r'Vendedor\s*([^\n]+?)(?:\s*Validade|$)',
        ],
        'date': [
            r'Data:\s*(\d{2}/\d{2}/\d{2})',
            r'Data\s*[-:]\s*(\d{2}/\d{2}/\d{2})',
            r'Data\s*(\d{2}/\d{2}/\d{2})',
        ],
        'total_value': [
            r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
            r'TOTAL\s*R\$\s*([\d\.,]+)',
            r'R\$\s*([\d\.,]+)',
        ],
    }
    
    print("TESTANDO PADRÕES ATUAIS:")
    for pattern_name, pattern in current_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        print(f"{pattern_name}: {matches}")
    
    print("\nTESTANDO PADRÕES FLEXÍVEIS:")
    for pattern_name, patterns in flexible_patterns.items():
        print(f"\n{pattern_name}:")
        for i, pattern in enumerate(patterns):
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            print(f"  Pattern {i+1}: {matches}")

def suggest_improvements(text):
    """Sugere melhorias baseadas na análise do texto"""
    print("\n" + "="*60)
    print("SUGESTÕES DE MELHORIAS")
    print("="*60)
    
    lines = text.split('\n')
    print("LINHAS DO TEXTO:")
    for i, line in enumerate(lines, 1):
        print(f"{i:2d}: {repr(line)}")
    
    print("\nPROCURANDO PADRÕES ESPECÍFICOS:")
    
    # Procurar por números que podem ser orçamento
    numbers = re.findall(r'\d+', text)
    print(f"Números encontrados: {numbers}")
    
    # Procurar por valores monetários
    money_patterns = [
        r'R\$\s*[\d\.,]+',
        r'[\d\.,]+',
    ]
    
    for pattern in money_patterns:
        matches = re.findall(pattern, text)
        print(f"Valores monetários ({pattern}): {matches}")
    
    # Procurar por estruturas de item
    item_patterns = [
        r'\d+\s*[\/\s]+.*?-->.*?[\/\s]+.*?[\/\s]+\d+',
        r'\d+.*?-->.*?UN.*?\d+',
        r'\d+.*?/.*?-->.*?/.*?UN.*?/.*?\d+',
    ]
    
    for pattern in item_patterns:
        matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
        print(f"Itens ({pattern}): {matches}")

def main():
    if len(sys.argv) != 2:
        print("Uso: python analyze_pdf.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    print(f"Analisando PDF: {pdf_path}")
    
    # Análise com pdfplumber
    analyze_pdf_with_pdfplumber(pdf_path)
    
    # Análise com PyPDF2
    analyze_pdf_with_pypdf2(pdf_path)
    
    # Extrair texto para análise de padrões
    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    full_text += page_text + "\n"
            
            if full_text:
                analyze_patterns(full_text)
                suggest_improvements(full_text)
    except Exception as e:
        print(f"Erro na análise de padrões: {e}")

if __name__ == "__main__":
    main()