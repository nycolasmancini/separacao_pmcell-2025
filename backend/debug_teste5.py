#!/usr/bin/env python3
"""
Debug script specifically for Teste 5.pdf that has text extraction artifacts.
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import pdfplumber
import re

def analyze_teste5_raw_text(pdf_path: str):
    """Analisa o texto bruto extraído do PDF."""
    print("ANÁLISE DO TEXTO BRUTO - TESTE 5")
    print("="*50)
    
    # Extrair texto bruto
    with pdfplumber.open(pdf_path) as pdf:
        raw_text = ""
        for page_num, page in enumerate(pdf.pages, 1):
            page_text = page.extract_text()
            if page_text:
                print(f"\n--- PÁGINA {page_num} ---")
                print(page_text[:500] + "..." if len(page_text) > 500 else page_text)
                raw_text += page_text + "\n"
    
    print(f"\n{'='*50}")
    print("ANÁLISE DE PROBLEMAS:")
    
    # Procurar por padrões de item
    lines = raw_text.split('\n')
    item_candidates = []
    
    for i, line in enumerate(lines):
        # Procura linhas que começam com código de 5 dígitos
        if re.match(r'^\d{5}', line.strip()):
            item_candidates.append((i, line.strip()))
            
    print(f"\nLinhas candidatas a itens ({len(item_candidates)}):")
    for line_num, line in item_candidates[:10]:  # Primeiros 10
        print(f"  {line_num}: {line}")
    
    # Verificar se há quebras de linha problemáticas
    print(f"\nVerificando estrutura de itens...")
    
    # Tentar juntar linhas quebradas
    cleaned_lines = []
    current_item = ""
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Se começa com código de 5 dígitos, é início de novo item
        if re.match(r'^\d{5}', line):
            if current_item:
                cleaned_lines.append(current_item)
            current_item = line
        else:
            # Se já tem item em construção, pode ser continuação
            if current_item and not re.match(r'^(Orçamento|Cliente|Vendedor|Data|VALOR)', line):
                current_item += " " + line
    
    # Adiciona último item
    if current_item:
        cleaned_lines.append(current_item)
    
    print(f"\nItens após limpeza ({len(cleaned_lines)}):")
    for i, item in enumerate(cleaned_lines[:10], 1):
        print(f"  {i}: {item}")
    
    return cleaned_lines

def test_improved_text_cleaning():
    """Testa limpeza melhorada de texto."""
    print(f"\n{'='*50}")
    print("TESTE DE LIMPEZA MELHORADA")
    
    # Simular texto problemático baseado na análise
    problematic_text = """07                                                                                                                    Orçamento Nº : 27890                                                        Data: 13/07/24 
/ FONE ADAPTADOR -> AP 20W SEM CAIXA / UN / 40 / 12,00 / 480,00
00970 / CABO USB -> TYPE C PARA IPHONE / UN / 30 / 8,00 / 240,00"""
    
    print("Texto problemático:")
    print(problematic_text)
    
    # Aplicar limpeza
    lines = problematic_text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Ignorar linhas que parecem ser cabeçalho
        if re.search(r'Orçamento\s*N[ºo°]?', line):
            continue
            
        # Procurar por padrão de item válido
        # Deve ter: código / referência / UN / quantidade / preço / total
        if re.search(r'\d+\s*/.*?/\s*UN\s*/\s*\d+\s*/\s*[\d,\.]+\s*/\s*[\d,\.]+', line):
            cleaned_lines.append(line)
    
    print(f"\nLinhas limpas:")
    for line in cleaned_lines:
        print(f"  {line}")
    
    return cleaned_lines

def create_enhanced_text_cleaner():
    """Cria função melhorada de limpeza de texto."""
    print(f"\n{'='*50}")
    print("FUNÇÃO DE LIMPEZA APRIMORADA")
    
    def clean_pdf_text(raw_text: str) -> str:
        """
        Limpa texto de PDF removendo artefatos de extração.
        """
        lines = raw_text.split('\n')
        cleaned_lines = []
        current_item = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ignorar linhas de cabeçalho/rodapé
            skip_patterns = [
                r'^Orçamento\s*N[ºo°]?',  # Cabeçalho
                r'^Data:',                 # Data no cabeçalho
                r'^Cliente:',             # Campo cliente
                r'^Vendedor:',            # Campo vendedor
                r'^VALOR\s+A\s+PAGAR',    # Total
                r'^\s*\d+\s*$',           # Números isolados
                r'^[A-Z\s]{20,}$',        # Texto em maiúscula muito longo
            ]
            
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line):
                    should_skip = True
                    break
            
            if should_skip:
                continue
            
            # Se começa com código de 5 dígitos seguido de /, é início de item
            if re.match(r'^\d{5}\s*/', line):
                if current_item:
                    cleaned_lines.append(current_item)
                current_item = line
            elif current_item and re.search(r'/\s*UN\s*/', line):
                # Linha contém /UN/, provavelmente é continuação do item
                current_item += " " + line
            elif current_item and not re.match(r'^\d{5}', line):
                # Possível continuação de item
                current_item += " " + line
            elif re.search(r'\d+\s*/.*?/\s*UN\s*/\s*\d+', line):
                # Linha completa de item
                cleaned_lines.append(line)
        
        # Adiciona último item se existe
        if current_item:
            cleaned_lines.append(current_item)
        
        return '\n'.join(cleaned_lines)
    
    # Teste com exemplo
    test_text = """07                                     Orçamento Nº : 27890                Data: 13/07/24
/ FONE ADAPTADOR -> AP 20W SEM CAIXA / UN / 40 / 12,00 / 480,00
Cliente: JOÃO DA SILVA
00970 / CABO USB -> TYPE C PARA IPHONE / UN / 30 / 8,00 / 240,00
VALOR A PAGAR R$ 720,00"""
    
    print("Texto de entrada:")
    print(test_text)
    
    cleaned = clean_pdf_text(test_text)
    print("\nTexto limpo:")
    print(cleaned)
    
    return clean_pdf_text

def main():
    if len(sys.argv) != 2:
        print("Uso: python debug_teste5.py <caminho_do_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    # Análise do texto bruto
    cleaned_lines = analyze_teste5_raw_text(pdf_path)
    
    # Teste de limpeza
    test_improved_text_cleaning()
    
    # Criar função de limpeza aprimorada
    clean_function = create_enhanced_text_cleaner()
    
    print(f"\n{'='*50}")
    print("PRÓXIMOS PASSOS:")
    print("1. Implementar limpeza de texto no PDFParser")
    print("2. Adicionar filtros para remover artefatos de cabeçalho")
    print("3. Melhorar junção de linhas quebradas")
    print("4. Testar com PDF real")

if __name__ == "__main__":
    main()