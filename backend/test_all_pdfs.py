#!/usr/bin/env python3
"""
Script para testar todos os PDFs e verificar se houve regressão.
"""

import sys
from pathlib import Path
from app.services.pdf_parser import PDFParser

def test_all_pdfs():
    """Testa todos os PDFs fornecidos."""
    pdf_files = [
        "/Users/nycolasmancini/Downloads/Tste 1.pdf",
        "/Users/nycolasmancini/Downloads/Teste 2.pdf", 
        "/Users/nycolasmancini/Downloads/Teste 3.pdf",
        "/Users/nycolasmancini/Downloads/Teste 4.pdf",
        "/Users/nycolasmancini/Downloads/Teste 5.pdf",
        "/Users/nycolasmancini/Downloads/Teste 6.pdf"
    ]
    
    # Resultados esperados baseados nos testes de integração
    expected_results = {
        "Tste 1.pdf": {"order_number": "0", "has_issues": True},  # Número 0 é suspeito
        "Teste 2.pdf": {"order_number": "27772", "min_items": 4},
        "Teste 3.pdf": {"order_number": "27771", "min_items": 4}, 
        "Teste 4.pdf": {"order_number": "27769", "min_items": 20},
        "Teste 5.pdf": {"order_number": "27766", "min_items": 45},
        "Teste 6.pdf": {"order_number": "27742", "min_items": 10}
    }
    
    parser = PDFParser()
    print("TESTE ABRANGENTE DE TODOS OS PDFs")
    print("="*60)
    
    all_passed = True
    
    for pdf_path in pdf_files:
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ Arquivo não encontrado: {pdf_path}")
            all_passed = False
            continue
            
        print(f"\n📄 TESTANDO: {pdf_file.name}")
        print("-" * 40)
        
        try:
            # Extrair dados
            result = parser.extract(pdf_file)
            
            # Obter expectativas
            expected = expected_results.get(pdf_file.name, {})
            
            # Verificar número do pedido
            order_number = result.get('order_number')
            expected_order = expected.get('order_number')
            
            if expected_order and order_number != expected_order:
                print(f"⚠️  Número do pedido: esperado {expected_order}, obtido {order_number}")
                if expected.get('has_issues'):
                    print("   (Este PDF tem problemas conhecidos)")
                else:
                    all_passed = False
            else:
                print(f"✅ Número do pedido: {order_number}")
            
            # Verificar itens
            items_count = len(result.get('items', []))
            min_items = expected.get('min_items', 1)
            
            if items_count >= min_items:
                print(f"✅ Itens extraídos: {items_count} (esperado mínimo: {min_items})")
            else:
                print(f"❌ Itens extraídos: {items_count} (esperado mínimo: {min_items})")
                all_passed = False
            
            # Verificar outros campos obrigatórios
            client = result.get('client_name')
            seller = result.get('seller_name') 
            date = result.get('order_date')
            total = result.get('total_value')
            
            print(f"   Cliente: {client}")
            print(f"   Vendedor: {seller}")
            print(f"   Data: {date}")
            print(f"   Total: R$ {total}")
            
            # Mostrar primeiros itens como amostra
            if items_count > 0:
                print(f"   Primeiros itens:")
                for i, item in enumerate(result['items'][:3], 1):
                    code = item.get('product_code')
                    name = item.get('product_name', '')[:30] + "..." if len(item.get('product_name', '')) > 30 else item.get('product_name', '')
                    print(f"     {i}. {code} - {name}")
                if items_count > 3:
                    print(f"     ... e mais {items_count - 3} itens")
            
        except Exception as e:
            print(f"❌ ERRO: {str(e)}")
            all_passed = False
    
    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("Nenhuma regressão detectada nos PDFs testados.")
    else:
        print("💥 ALGUNS TESTES FALHARAM!")
        print("Há regressões que precisam ser corrigidas.")
    print("="*60)
    
    return all_passed

if __name__ == "__main__":
    test_all_pdfs()