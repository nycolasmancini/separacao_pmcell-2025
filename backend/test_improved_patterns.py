#!/usr/bin/env python3
"""
Script para testar padrões melhorados de extração de PDF.
"""

import re
from typing import Dict, List, Any, Optional

# Texto extraído do PDF real
SAMPLE_TEXT = """PMCELL São Paulo
V. Zabin Tecnologia e Comercio Eireeli
CNPJ: 29.734.462/0003-86
I.E: 130.745.005.110
Rua Comendador Abdo Schahin, 62
Orçamento Nº: 27820
Código: 002633 Data: 11/07/25 Condição de Pagto:
Cliente: 20.517.107 MARCIO APARECIDO DE SANTANA Forma de Pagto:
Vendedor: NYCOLAS HENDRIGO MANCINI Validade do Orçamento: 11/07/25 - 0 dia(s)
Código Produto Unid. Quant. Valor Total
00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00
03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00
00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00
00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00
VALOR TOTAL R$ 2.380,00
DESCONTO R$ 0,00
VALOR A PAGAR R$ 2.380,00
Página 1"""

# Padrões atuais
CURRENT_PATTERNS = {
    'order_number': r'Orçamento\s*N[ºo°]?:?\s*(\d+)',
    'client': r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',
    'seller': r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',
    'date': r'Data:\s*(\d{2}/\d{2}/\d{2})',
    'total_value': r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',
    'items': r'(\d+)\s*[\/\s]+([A-Z0-9\s\-]+?)\s*-->\s*(.+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)'
}

# Padrões melhorados
IMPROVED_PATTERNS = {
    'order_number': [
        r'Orçamento\s*N[ºo°]?:?\s*(\d+)',  # Padrão original
        r'Or[çc]amento\s*[-:]*\s*(\d+)',   # Variações de acentuação
        r'N[ºo°]\s*[:]*\s*(\d+)',          # Apenas número
    ],
    'client': [
        r'Cliente:\s*([^\n]+?)(?:\s*Forma\s*de\s*Pagto|$)',  # Padrão original
        r'Cliente\s*[-:]\s*([^\n]+?)(?:\s*Forma|$)',         # Variações de separador
        r'Cliente\s+([^\n]+?)(?:\s*Forma|$)',                # Apenas espaço
    ],
    'seller': [
        r'Vendedor:\s*([^\n]+?)(?:\s*Validade\s*do\s*Orçamento|$)',  # Padrão original
        r'Vendedor\s*[-:]\s*([^\n]+?)(?:\s*Validade|$)',             # Variações de separador
        r'Vendedor\s+([^\n]+?)(?:\s*Validade|$)',                    # Apenas espaço
    ],
    'date': [
        r'Data:\s*(\d{2}/\d{2}/\d{2})',     # Padrão original
        r'Data\s*[-:]\s*(\d{2}/\d{2}/\d{2})', # Variações de separador
        r'(\d{2}/\d{2}/\d{2})',             # Apenas data
    ],
    'total_value': [
        r'VALOR\s+A\s+PAGAR\s*R\$\s*([\d\.,]+)',  # Padrão original
        r'TOTAL\s*R\$\s*([\d\.,]+)',              # Alternativo
        r'VALOR\s*TOTAL\s*R\$\s*([\d\.,]+)',      # Variação
    ],
    'items': [
        # Padrão original (com -->)
        r'(\d+)\s*[\/\s]+([^\/]+?)\s*-->\s*([^\/]+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)',
        # Padrão novo (sem --> obrigatório, permite /)
        r'(\d+)\s*[\/\s]+([^\/]+?)\s*(?:-->|\/)\s*([^\/]+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)',
        # Padrão mais flexível (permite diferentes separadores)
        r'(\d+)\s*[\/\s]+([^\/]+?)\s*[\/\-]*\s*([^\/]+?)\s*[\/\s]+UN\s*[\/\s]+(\d+)\s*[\/\s]+([\d,\.]+)\s*[\/\s]+([\d,\.]+)',
    ]
}

def test_pattern(text: str, pattern: str, description: str) -> List[str]:
    """Testa um padrão específico."""
    matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
    print(f"{description}: {matches}")
    return matches

def test_current_patterns():
    """Testa os padrões atuais."""
    print("="*60)
    print("TESTANDO PADRÕES ATUAIS")
    print("="*60)
    
    results = {}
    for name, pattern in CURRENT_PATTERNS.items():
        matches = test_pattern(SAMPLE_TEXT, pattern, f"Current {name}")
        results[name] = matches
    
    return results

def test_improved_patterns():
    """Testa os padrões melhorados."""
    print("\n" + "="*60)
    print("TESTANDO PADRÕES MELHORADOS")
    print("="*60)
    
    results = {}
    for name, patterns in IMPROVED_PATTERNS.items():
        print(f"\n--- {name.upper()} ---")
        field_results = []
        
        for i, pattern in enumerate(patterns, 1):
            matches = test_pattern(SAMPLE_TEXT, pattern, f"Pattern {i}")
            if matches:
                field_results.extend(matches)
        
        # Remove duplicatas mantendo ordem
        unique_results = list(dict.fromkeys(field_results))
        results[name] = unique_results
        print(f"Combined results: {unique_results}")
    
    return results

def test_items_specifically():
    """Testa especificamente os padrões de itens."""
    print("\n" + "="*60)
    print("TESTE ESPECÍFICO DE ITENS")
    print("="*60)
    
    # Linhas de itens individuais para teste
    item_lines = [
        "00815 / PELICULA 3D --> IP XR / 11 / UN / 600 / 0,90 / 540,00",
        "03242 / PELICULA 3D --> SAM A56 / UN / 500 / 1,20 / 600,00",
        "00852 / PELICULA 3D --> MOTO G55 / UN / 600 / 0,90 / 540,00",
        "00267 / LIMPA TELA (1 - 2) - 400 UNIDADES / UN / 50 / 14,00 / 700,00"
    ]
    
    for i, line in enumerate(item_lines, 1):
        print(f"\n--- ITEM {i} ---")
        print(f"Linha: {line}")
        
        # Testa padrão atual
        current_pattern = CURRENT_PATTERNS['items']
        current_match = re.findall(current_pattern, line, re.IGNORECASE)
        print(f"Padrão atual: {current_match}")
        
        # Testa padrões melhorados
        for j, pattern in enumerate(IMPROVED_PATTERNS['items'], 1):
            matches = re.findall(pattern, line, re.IGNORECASE)
            print(f"Padrão melhorado {j}: {matches}")

def compare_results(current: Dict, improved: Dict):
    """Compara resultados dos padrões."""
    print("\n" + "="*60)
    print("COMPARAÇÃO DE RESULTADOS")
    print("="*60)
    
    for field in current.keys():
        print(f"\n--- {field.upper()} ---")
        print(f"Atual:     {current[field]}")
        print(f"Melhorado: {improved[field]}")
        
        # Análise
        current_count = len(current[field]) if isinstance(current[field], list) else (1 if current[field] else 0)
        improved_count = len(improved[field]) if isinstance(improved[field], list) else (1 if improved[field] else 0)
        
        if improved_count > current_count:
            print(f"✅ MELHORIA: {improved_count - current_count} itens a mais")
        elif improved_count == current_count:
            print("✓ Mantém resultados")
        else:
            print(f"⚠️  PERDA: {current_count - improved_count} itens a menos")

def main():
    print("TESTE DE PADRÕES MELHORADOS PARA PDF")
    print("Testando com PDF real: Orçamento 27820")
    
    # Testa padrões atuais
    current_results = test_current_patterns()
    
    # Testa padrões melhorados
    improved_results = test_improved_patterns()
    
    # Teste específico de itens
    test_items_specifically()
    
    # Compara resultados
    compare_results(current_results, improved_results)
    
    print(f"\n{'='*60}")
    print("RESUMO")
    print(f"{'='*60}")
    print("✅ Padrões básicos funcionam bem")
    print("⚠️  Padrão de itens precisa melhorar para capturar item 00267")
    print("🎯 Objetivo: 100% de captura dos itens")

if __name__ == "__main__":
    main()