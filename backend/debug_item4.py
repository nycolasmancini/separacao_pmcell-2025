#!/usr/bin/env python3
"""
Debug específico para o item 4 que não está sendo capturado.
"""

import re

# Item problemático
ITEM4 = "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"

def analyze_item4():
    """Analisa em detalhes o item 4."""
    print("ANÁLISE DETALHADA DO ITEM 4")
    print("="*50)
    print(f"Linha: {ITEM4}")
    print()
    
    # Separar por /
    parts = ITEM4.split(' / ')
    print("PARTES SEPARADAS POR ' / ':")
    for i, part in enumerate(parts):
        print(f"  {i}: '{part}'")
    print()
    
    # Estrutura esperada:
    # 0: código (00267)
    # 1: referência (LIMPA TELA (1 - 2) - 400 UNIDADES)  
    # 2: unidade (UN)
    # 3: quantidade (50)
    # 4: preço unitário (14,00)
    # 5: preço total (700,00)
    
    print("ESTRUTURA ESPERADA:")
    print("  0: código")
    print("  1: referência completa (sem descrição separada)")
    print("  2: unidade") 
    print("  3: quantidade")
    print("  4: preço unitário")
    print("  5: preço total")
    print()
    
    print("PROBLEMA IDENTIFICADO:")
    print("- Este item NÃO tem '-->' separando referência de descrição")
    print("- A referência É a descrição completa")
    print("- Padrão atual espera sempre 3 partes: código, referência, descrição")
    print("- Este item tem apenas 2 partes: código, referência_completa")

def test_new_patterns():
    """Testa novos padrões que lidam com este caso."""
    print(f"\n{'='*50}")
    print("TESTANDO NOVOS PADRÕES:")
    
    # Padrão que lida com referência sem descrição separada
    patterns = [
        # Padrão original (falha)
        r'(\d+)\s*/\s*([^/]+?)\s*-->\s*([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        
        # Padrão que aceita referência sem '-->' (trata como referência+descrição em um)
        r'(\d+)\s*/\s*([^/]+?)\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
        
        # Padrão híbrido que captura ambos os casos
        r'(\d+)\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)',
    ]
    
    descriptions = [
        "Original (só com -->)",
        "Sem --> (referência completa)",
        "Híbrido (com ou sem -->)"
    ]
    
    test_items = [
        "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
        "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00",
        "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00", 
        "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
    ]
    
    for i, (pattern, desc) in enumerate(zip(patterns, descriptions), 1):
        print(f"\n--- PADRÃO {i}: {desc} ---")
        print(f"Regex: {pattern}")
        
        total_captured = 0
        for j, item in enumerate(test_items, 1):
            matches = re.findall(pattern, item, re.IGNORECASE)
            print(f"  Item {j}: {matches}")
            if matches:
                total_captured += 1
        
        print(f"  Total: {total_captured}/4 itens")

def create_final_pattern():
    """Cria o padrão final que funciona para todos os casos."""
    print(f"\n{'='*50}")
    print("PADRÃO FINAL RECOMENDADO:")
    
    # Este padrão captura:
    # - Grupo 1: código
    # - Grupo 2: referência/modelo  
    # - Grupo 3: descrição (se existe -->, senão fica vazio)
    # - Grupo 4: quantidade
    # - Grupo 5: preço unitário
    # - Grupo 6: preço total
    
    final_pattern = r'(\d+)\s*/\s*([^/]+?)(?:\s*-->\s*([^/]+?))?\s*/\s*UN\s*/\s*(\d+)\s*/\s*([\d,\.]+)\s*/\s*([\d,\.]+)'
    
    print(f"Padrão: {final_pattern}")
    print()
    print("EXPLICAÇÃO:")
    print("- (\\d+): captura código")
    print("- \\s*/\\s*: espaços + barra + espaços")
    print("- ([^/]+?): captura referência até próxima barra")
    print("- (?:\\s*-->\\s*([^/]+?))?: OPCIONAL - se tem '-->', captura descrição")
    print("- \\s*/\\s*UN\\s*/\\s*: ' / UN / '")
    print("- (\\d+): quantidade")
    print("- \\s*/\\s*([\d,\\.]+): preço unitário")
    print("- \\s*/\\s*([\d,\\.]+): preço total")
    print()
    
    # Teste final
    print("TESTE FINAL:")
    test_items = [
        "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
        "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00",
        "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00",
        "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
    ]
    
    total_captured = 0
    for i, item in enumerate(test_items, 1):
        matches = re.findall(final_pattern, item, re.IGNORECASE)
        print(f"Item {i}: {matches}")
        if matches:
            total_captured += 1
            
            # Processa resultado
            match = matches[0]
            code = match[0]
            reference = match[1]
            description = match[2] if match[2] else reference  # Se não tem descrição, usa referência
            quantity = match[3]
            unit_price = match[4]
            total_price = match[5]
            
            print(f"  Processado: código={code}, ref={reference}, desc={description}, qtd={quantity}")
    
    print(f"\nRESULTADO: {total_captured}/4 itens capturados ✅")
    
    return final_pattern

def main():
    analyze_item4()
    test_new_patterns()
    final_pattern = create_final_pattern()
    
    print(f"\n{'='*50}")
    print("RECOMENDAÇÃO:")
    print("Usar o padrão híbrido que funciona com e sem '-->'")
    print("Tratar descrição vazia usando referência como fallback")

if __name__ == "__main__":
    main()