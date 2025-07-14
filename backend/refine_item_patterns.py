#!/usr/bin/env python3
"""
Script para refinar especificamente os padrões de itens.
"""

import re

# Linhas de teste reais
ITEM_LINES = [
    "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
    "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00", 
    "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00",
    "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
]

def test_item_pattern(pattern: str, description: str):
    """Testa um padrão específico de item."""
    print(f"\n--- {description} ---")
    print(f"Padrão: {pattern}")
    
    total_matches = 0
    for i, line in enumerate(ITEM_LINES, 1):
        matches = re.findall(pattern, line, re.IGNORECASE)
        print(f"Item {i}: {matches}")
        if matches:
            total_matches += 1
    
    print(f"Total capturado: {total_matches}/4 itens")
    return total_matches

def main():
    print("REFINAMENTO DE PADRÕES DE ITENS")
    print("="*50)
    
    # Padrão atual
    current_pattern = r'(\d+)\s*[\/\s]+([A-Z0-9\s\-]+?)\s*-->\s*(.+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)'
    test_item_pattern(current_pattern, "PADRÃO ATUAL")
    
    # Análise das linhas
    print(f"\n{'='*50}")
    print("ANÁLISE DAS LINHAS:")
    for i, line in enumerate(ITEM_LINES, 1):
        print(f"{i}: {line}")
    
    print(f"\n{'='*50}")
    print("OBSERVAÇÕES:")
    print("- Linhas 1-3: Usam ' --> ' como separador")
    print("- Linha 4: Não usa '-->', apenas ' / '")
    print("- Todas têm estrutura: codigo / referencia [-->|/] descricao / UN / qtd / preco_unit / preco_total")
    
    # Padrões refinados
    print(f"\n{'='*50}")
    print("TESTANDO PADRÕES REFINADOS:")
    
    # Padrão 1: Torna --> opcional
    pattern1 = r'(\d+)\s*[\/\s]+([^\/]+?)\s*(?:-->\s*)?([^\/]+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)'
    test_item_pattern(pattern1, "PADRÃO 1: --> opcional")
    
    # Padrão 2: Mais específico com grupos não-capturantes
    pattern2 = r'(\d+)\s*/\s*([^/]+?)\s*(?:-->\s*|\s*/\s*)([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    test_item_pattern(pattern2, "PADRÃO 2: / como separador principal")
    
    # Padrão 3: Híbrido mais flexível
    pattern3 = r'(\d+)\s*/\s*([^/]+?)\s*(?:-->\s*([^/]+?)\s*|\s*/\s*([^/]+?)\s*)/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    print(f"\n--- PADRÃO 3: Híbrido com grupos condicionais ---")
    print(f"Padrão: {pattern3}")
    
    for i, line in enumerate(ITEM_LINES, 1):
        matches = re.findall(pattern3, line, re.IGNORECASE)
        print(f"Item {i}: {matches}")
        
    # Padrão 4: Simples e efetivo
    pattern4 = r'(\d+)\s*/\s*([^/]+?)\s*(?:-->|/)\s*([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    test_item_pattern(pattern4, "PADRÃO 4: Simples com --> ou /")
    
    # Padrão 5: O mais robusto
    pattern5 = r'(\d+)\s*/\s*([^/]+?)\s*(?:-->\s*|/\s*)([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    test_item_pattern(pattern5, "PADRÃO 5: Robusto com espaços flexíveis")

if __name__ == "__main__":
    main()