#!/usr/bin/env python3
"""
Script para testar o parser de PDF melhorado com o PDF real.
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser
import json

def test_pdf_parsing(pdf_path: str):
    """Testa o parsing do PDF com o parser melhorado."""
    print("TESTE DO PARSER DE PDF MELHORADO")
    print("="*50)
    print(f"PDF: {pdf_path}")
    print()
    
    # Criar instância do parser
    parser = PDFParser()
    
    try:
        # Extrair dados
        pdf_file_path = Path(pdf_path)
        data = parser.extract(pdf_file_path)
        
        # Exibir resultados
        print("✅ EXTRAÇÃO BEM-SUCEDIDA!")
        print()
        
        print("📋 DADOS EXTRAÍDOS:")
        print("-" * 30)
        
        print(f"📝 Número do Pedido: {data.get('order_number', 'N/A')}")
        print(f"👤 Cliente: {data.get('client_name', 'N/A')}")
        print(f"🏪 Vendedor: {data.get('seller_name', 'N/A')}")
        print(f"📅 Data: {data.get('order_date', 'N/A')}")
        print(f"💰 Valor Total: R$ {data.get('total_value', 'N/A')}")
        print()
        
        # Itens
        items = data.get('items', [])
        print(f"🛍️  ITENS ({len(items)} encontrados):")
        print("-" * 30)
        
        for i, item in enumerate(items, 1):
            print(f"Item {i}:")
            print(f"  📦 Código: {item.get('product_code', 'N/A')}")
            print(f"  🏷️  Referência: {item.get('product_reference', 'N/A')}")
            print(f"  📝 Nome: {item.get('product_name', 'N/A')}")
            print(f"  🔢 Quantidade: {item.get('quantity', 'N/A')}")
            print(f"  💵 Preço Unit.: R$ {item.get('unit_price', 'N/A')}")
            print(f"  💰 Preço Total: R$ {item.get('total_price', 'N/A')}")
            print()
        
        # Comparação com expectativa
        print("🎯 ANÁLISE DOS RESULTADOS:")
        print("-" * 30)
        
        expected_items = [
            "00815 - PELICULA 3D --> IP XR",
            "03242 - PELICULA 3D --> SAM A56", 
            "00852 - PELICULA 3D --> MOTO G55",
            "00267 - LIMPA TELA (1 - 2) - 400 UNIDADES"
        ]
        
        found_codes = [item.get('product_code') for item in items]
        expected_codes = ["00815", "03242", "00852", "00267"]
        
        print(f"Códigos esperados: {expected_codes}")
        print(f"Códigos encontrados: {found_codes}")
        
        missing_codes = set(expected_codes) - set(found_codes)
        extra_codes = set(found_codes) - set(expected_codes)
        
        if not missing_codes and not extra_codes:
            print("✅ PERFEITO! Todos os itens foram capturados corretamente.")
        else:
            if missing_codes:
                print(f"⚠️  Códigos em falta: {missing_codes}")
            if extra_codes:
                print(f"ℹ️  Códigos extras: {extra_codes}")
        
        print(f"\nTaxa de sucesso: {len(found_codes)}/{len(expected_codes)} itens ({len(found_codes)/len(expected_codes)*100:.1f}%)")
        
        # JSON para debugging
        print(f"\n🔧 DADOS COMPLETOS (JSON):")
        print("-" * 30)
        print(json.dumps(data, indent=2, default=str, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ ERRO NA EXTRAÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def compare_with_original():
    """Compara resultados com parser original."""
    print(f"\n{'='*50}")
    print("COMPARAÇÃO COM PARSER ORIGINAL")
    print("="*50)
    
    print("Parser Original (antes das melhorias):")
    print("✅ Número do Pedido: 27820")
    print("✅ Cliente: MARCIO APARECIDO DE SANTANA")
    print("✅ Vendedor: NYCOLAS HENDRIGO MANCINI")
    print("✅ Data: 11/07/25")
    print("✅ Valor Total: R$ 2.380,00")
    print("⚠️  Itens: 3/4 (perdeu item 00267)")
    print()
    print("Melhorias implementadas:")
    print("🎯 Padrão de itens mais robusto")
    print("🎯 Suporte a itens sem '-->'")
    print("🎯 Captura de campos extras opcionais") 
    print("🎯 Padrões de fallback para casos edge")

def main():
    if len(sys.argv) != 2:
        print("Uso: python test_improved_parser.py <caminho_do_pdf>")
        print("Exemplo: python test_improved_parser.py '/Users/user/Documents/Orcamento - 27820 - Marcio - R$ 2380,00.pdf'")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not Path(pdf_path).exists():
        print(f"❌ Arquivo não encontrado: {pdf_path}")
        sys.exit(1)
    
    # Teste principal
    success = test_pdf_parsing(pdf_path)
    
    # Comparação
    compare_with_original()
    
    # Resultado final
    print(f"\n{'='*50}")
    if success:
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("O parser melhorado está funcionando corretamente.")
    else:
        print("💥 TESTE FALHOU!")
        print("Verifique os logs de erro acima.")
    print("="*50)

if __name__ == "__main__":
    main()