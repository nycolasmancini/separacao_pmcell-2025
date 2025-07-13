#!/usr/bin/env python3
"""
Script para analisar PDFs de amostra e entender a estrutura dos dados
"""

import os
import sys
import PyPDF2
import pdfplumber
import re
from pathlib import Path

def extract_with_pypdf2(pdf_path):
    """Extrai texto usando PyPDF2"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return f"Erro PyPDF2: {e}"

def extract_with_pdfplumber(pdf_path):
    """Extrai texto usando pdfplumber (mais preciso)"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text
    except Exception as e:
        return f"Erro pdfplumber: {e}"

def analyze_pdf_structure(text, filename):
    """Analisa a estrutura do PDF e identifica padrões"""
    print(f"\n{'='*60}")
    print(f"ANÁLISE: {filename}")
    print(f"{'='*60}")
    
    # Buscar informações do cliente
    cliente_patterns = [
        r'cliente[:\s]*([^\n]+)',
        r'razão social[:\s]*([^\n]+)',
        r'nome[:\s]*([^\n]+)',
    ]
    
    # Buscar número do orçamento/pedido
    orcamento_patterns = [
        r'orçamento[:\s]*([^\n]+)',
        r'pedido[:\s]*([^\n]+)',
        r'número[:\s]*([^\n]+)',
        r'n[ºo°\.]\s*([^\n]+)',
    ]
    
    # Buscar vendedor
    vendedor_patterns = [
        r'vendedor[:\s]*([^\n]+)',
        r'atendente[:\s]*([^\n]+)',
        r'representante[:\s]*([^\n]+)',
    ]
    
    # Buscar valor total
    valor_patterns = [
        r'total[:\s]*([R$\d\.,\s]+)',
        r'valor[:\s]*([R$\d\.,\s]+)',
        r'R\$\s*([\d\.,]+)',
    ]
    
    print("TEXTO COMPLETO:")
    print("-" * 40)
    print(text[:1000] + "..." if len(text) > 1000 else text)
    
    print("\nPADRÕES ENCONTRADOS:")
    print("-" * 40)
    
    # Procurar por cada padrão
    for pattern_name, patterns in [
        ("Cliente", cliente_patterns),
        ("Orçamento", orcamento_patterns), 
        ("Vendedor", vendedor_patterns),
        ("Valor", valor_patterns)
    ]:
        found = False
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                print(f"{pattern_name}: {matches}")
                found = True
                break
        if not found:
            print(f"{pattern_name}: NÃO ENCONTRADO")
    
    # Procurar por tabelas/itens (linhas que parecem produtos)
    lines = text.split('\n')
    produtos_candidatos = []
    
    for line in lines:
        line = line.strip()
        # Procurar linhas que parecem ter código, descrição, quantidade, valor
        if re.search(r'\d+.*\d+[,\.]\d{2}', line):  # linha com números e valor monetário
            produtos_candidatos.append(line)
    
    if produtos_candidatos:
        print(f"\nPRODUTOS CANDIDATOS ({len(produtos_candidatos)}):")
        print("-" * 40)
        for i, produto in enumerate(produtos_candidatos[:10]):  # primeiros 10
            print(f"{i+1}. {produto}")
        if len(produtos_candidatos) > 10:
            print(f"... e mais {len(produtos_candidatos) - 10} itens")

def main():
    pdf_files = [
        "/Users/nycolasmancini/Downloads/Teste 2.pdf",
        "/Users/nycolasmancini/Downloads/Teste 3.pdf", 
        "/Users/nycolasmancini/Downloads/Teste 4.pdf",
        "/Users/nycolasmancini/Downloads/Teste 5.pdf",
        "/Users/nycolasmancini/Downloads/Teste 6.pdf"
    ]
    
    for pdf_path in pdf_files:
        if os.path.exists(pdf_path):
            filename = os.path.basename(pdf_path)
            
            # Tentar com pdfplumber primeiro
            text = extract_with_pdfplumber(pdf_path)
            if "Erro" in text:
                # Fallback para PyPDF2
                text = extract_with_pypdf2(pdf_path)
            
            analyze_pdf_structure(text, filename)
        else:
            print(f"Arquivo não encontrado: {pdf_path}")

if __name__ == "__main__":
    main()