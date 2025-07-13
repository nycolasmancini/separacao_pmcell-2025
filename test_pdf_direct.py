#!/usr/bin/env python3
"""Test PDF extraction directly with the updated parser"""
import sys
sys.path.append('/Users/nycolasmancini/Desktop/pmcell-separacao/backend')

from pathlib import Path
from app.services.pdf_parser import PDFParser

def test_pdf_extraction():
    pdf_path = Path("/Users/nycolasmancini/Desktop/pmcell-separacao/test_pdf.pdf")
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    print(f"Testing PDF extraction with: {pdf_path}")
    print("="*60)
    
    try:
        parser = PDFParser()
        data = parser.extract(pdf_path)
        
        print("✅ EXTRACTION SUCCESSFUL!")
        print("\n📊 EXTRACTED DATA:")
        print("-" * 40)
        print(f"Order Number: {data.get('order_number')}")
        print(f"Client: {data.get('client_name')}")
        print(f"Seller: {data.get('seller_name')}")
        print(f"Date: {data.get('order_date')}")
        print(f"Total Value: {data.get('total_value')}")
        print(f"Items Count: {len(data.get('items', []))}")
        
        print("\n📦 ITEMS:")
        print("-" * 40)
        for i, item in enumerate(data.get('items', []), 1):
            print(f"Item {i}:")
            print(f"  Code: {item.get('product_code')}")
            print(f"  Reference: {item.get('product_reference')}")
            print(f"  Name: {item.get('product_name')}")
            print(f"  Quantity: {item.get('quantity')}")
            print(f"  Unit Price: {item.get('unit_price')}")
            print(f"  Total: {item.get('total_price')}")
            print()
        
        print(f"Total items extracted: {len(data.get('items', []))}")
        
    except Exception as e:
        print(f"❌ EXTRACTION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pdf_extraction()