#!/usr/bin/env python3
"""
Debug específico para o item 1 que não está sendo capturado pelo padrão híbrido.
"""

import re

# Item 1 problemático
ITEM1 = "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00"

def analyze_item1():
    """Analisa em detalhes o item 1."""
    print("ANÁLISE DETALHADA DO ITEM 1")
    print("="*50)
    print(f"Linha: {ITEM1}")
    print()
    
    # Separar por /
    parts = ITEM1.split(' / ')
    print("PARTES SEPARADAS POR ' / ':")
    for i, part in enumerate(parts):
        print(f"  {i}: '{part}'")
    print()
    
    print("PROBLEMA IDENTIFICADO:")
    print("- Parte 1: 'PELICULA 3D --> IP XR'")
    print("- Parte 2: '11'") 
    print("- O padrão não consegue distinguir onde termina a descrição depois de '-->'")
    print("- '11' está sendo tratado como parte da descrição, não como valor separado")

def test_item1_specifically():
    """Testa padrões específicos para o item 1."""
    print(f"\n{'='*50}")
    print("TESTANDO PADRÕES PARA ITEM 1:")
    
    patterns = [
        # Padrão atual que falha
        r'(\d+)\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        
        # Padrão que espera estrutura específica: codigo / ref --> desc / info / UN / ...
        r'(\d+)\s*/\s*([^/]+?)\s*-->\s*([^/]+?)\s*/\s*([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        
        # Padrão mais específico para o caso com -->
        r'(\d+)\s*/\s*([^/]+?)\s*-->\s*([^/]+?)\s*/\s*(\d+)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        
        # Padrão que trata o 'extra' após --> como parte da estrutura
        r'(\d+)\s*/\s*([^/]+?)\s*-->\s*([^/]+?)(?:\s*/\s*(\d+))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
    ]
    
    descriptions = [
        "Híbrido original (falha)",
        "Com campo extra após descrição",
        "Específico para --> com número",
        "Híbrido com número opcional"
    ]
    
    for i, (pattern, desc) in enumerate(zip(patterns, descriptions), 1):
        print(f"\n--- PADRÃO {i}: {desc} ---")
        print(f"Regex: {pattern}")
        
        matches = re.findall(pattern, ITEM1, re.IGNORECASE)
        print(f"  Resultado: {matches}")

def analyze_all_items_structure():
    """Analisa a estrutura de todos os itens para entender padrão."""
    print(f"\n{'='*50}")
    print("ANÁLISE ESTRUTURAL DE TODOS OS ITENS:")
    
    items = [
        "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
        "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00",
        "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00",
        "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
    ]
    
    for i, item in enumerate(items, 1):
        print(f"\nItem {i}: {item}")
        parts = item.split(' / ')
        print(f"  Partes: {parts}")
        
        if '-->' in item:
            # Separar antes e depois de -->
            before_arrow = item.split(' --> ')[0]
            after_arrow = item.split(' --> ')[1]
            print(f"  Antes --\u003e: '{before_arrow}'")
            print(f"  Depois --\u003e: '{after_arrow}'")
            
            # Analisar estrutura após -->
            after_parts = after_arrow.split(' / ')
            print(f"  Partes após --\u003e: {after_parts}")
    
    print(f"\n{'='*50}")
    print("PADRÃO IDENTIFICADO:")
    print("Item 1: codigo / ref --> desc / extra / UN / qtd / preco_unit / preco_total")
    print("Item 2: codigo / ref --> desc / UN / qtd / preco_unit / preco_total") 
    print("Item 3: codigo / ref --> desc / UN / qtd / preco_unit / preco_total")
    print("Item 4: codigo / ref / UN / qtd / preco_unit / preco_total")
    print()
    print("PROBLEMA: Item 1 tem um campo EXTRA ('11') entre descrição e 'UN'")

def create_universal_pattern():
    """Cria um padrão universal que funciona para todos os casos."""
    print(f"\n{'='*50}")
    print("PADRÃO UNIVERSAL:")
    
    # Este padrão considera que pode haver campos extras opcionais
    universal_pattern = r'(\d+)\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*(?:/\s*([^/]*?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    
    print(f"Padrão: {universal_pattern}")
    print()
    print("GRUPOS:")
    print("1. Código")
    print("2. Referência")
    print("3. Descrição (se tem -->)")
    print("4. Campo extra (opcional)")
    print("5. Quantidade")
    print("6. Preço unitário")
    print("7. Preço total")
    print()
    
    items = [
        "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
        "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00",
        "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00",
        "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
    ]
    
    total_captured = 0
    for i, item in enumerate(items, 1):
        matches = re.findall(universal_pattern, item, re.IGNORECASE)
        print(f"Item {i}: {matches}")
        if matches:
            total_captured += 1
    
    print(f"\nRESULTADO: {total_captured}/4 itens ✅")
    
    # Teste mais simples - dividir em dois padrões
    print(f"\n{'='*50}")
    print("ALTERNATIVA: DOIS PADRÕES ESPECÍFICOS")
    
    pattern_with_arrow = r'(\d+)\s*/\s*([^/]+?)\s*-->\s*([^/]+?)(?:\s*/\s*([^/]+?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    pattern_without_arrow = r'(\d+)\s*/\s*([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    
    print("Padrão COM -->: ", pattern_with_arrow)
    print("Padrão SEM -->: ", pattern_without_arrow)
    print()
    
    total_with_arrow = 0
    total_without_arrow = 0
    
    for i, item in enumerate(items, 1):
        print(f"Item {i}:")
        if '-->' in item:
            matches = re.findall(pattern_with_arrow, item, re.IGNORECASE)
            print(f"  COM --\u003e: {matches}")
            if matches:
                total_with_arrow += 1
        else:
            matches = re.findall(pattern_without_arrow, item, re.IGNORECASE)
            print(f"  SEM --\u003e: {matches}")
            if matches:
                total_without_arrow += 1
    
    print(f"\nRESULTADO: {total_with_arrow + total_without_arrow}/4 itens ✅")

def main():
    analyze_item1()
    test_item1_specifically()
    analyze_all_items_structure()
    create_universal_pattern()

if __name__ == "__main__":
    main()