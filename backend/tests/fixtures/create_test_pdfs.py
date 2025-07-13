"""
Script para criar PDFs de teste válidos.
"""
import os
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def create_sample_order_pdf():
    """Cria um PDF de exemplo de pedido."""
    pdf_path = Path(__file__).parent / "pdfs" / "sample_order.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    # Cabeçalho
    c.setFont("Helvetica-Bold", 16)
    c.drawString(2*cm, height - 2*cm, "PMCELL SÃO PAULO")
    
    # Informações do pedido
    c.setFont("Helvetica", 12)
    y = height - 4*cm
    
    c.drawString(2*cm, y, "Orçamento Nº: 12345")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Data: 12/07/24")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Cliente: EMPRESA TESTE LTDA")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Vendedor: João Silva")
    y -= 1.5*cm
    
    # Produtos
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2*cm, y, "PRODUTOS:")
    y -= 0.7*cm
    
    c.setFont("Helvetica", 10)
    c.drawString(2*cm, y, "001 / REF-001 --> PRODUTO TESTE 1 / UN / 5 / 100,00 / 500,00")
    y -= 0.5*cm
    
    c.drawString(2*cm, y, "002 / REF-002 --> PRODUTO TESTE 2 / UN / 3 / 250,00 / 750,00")
    y -= 1.5*cm
    
    # Total
    c.setFont("Helvetica-Bold", 14)
    c.drawString(2*cm, y, "VALOR A PAGAR R$ 1.250,00")
    
    c.save()
    print(f"PDF criado: {pdf_path}")

def create_special_chars_pdf():
    """Cria um PDF com caracteres especiais."""
    pdf_path = Path(__file__).parent / "pdfs" / "special_chars.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica", 12)
    y = height - 2*cm
    
    c.drawString(2*cm, y, "Orçamento Nº: 99999")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Data: 01/01/25")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Cliente: JOSÉ AÇÚCAR & COMPANHIA LTDA")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Vendedor: María José")
    y -= 1*cm
    
    c.drawString(2*cm, y, "001 / REF-ÇÃO --> VÁLVULA CONEXÃO / UN / 1 / 150,00 / 150,00")
    y -= 1*cm
    
    c.drawString(2*cm, y, "VALOR A PAGAR R$ 150,00")
    
    c.save()
    print(f"PDF criado: {pdf_path}")

def create_multipage_pdf():
    """Cria um PDF com múltiplas páginas."""
    pdf_path = Path(__file__).parent / "pdfs" / "multipage.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    # Primeira página
    c.setFont("Helvetica", 12)
    y = height - 2*cm
    
    c.drawString(2*cm, y, "Orçamento Nº: 88888")
    y -= 0.7*cm
    c.drawString(2*cm, y, "Data: 15/07/24")
    y -= 0.7*cm
    c.drawString(2*cm, y, "Cliente: GRANDE EMPRESA LTDA")
    y -= 0.7*cm
    c.drawString(2*cm, y, "Vendedor: Carlos Silva")
    y -= 1*cm
    
    # Muitos itens
    for i in range(1, 16):
        c.drawString(2*cm, y, f"{i:03d} / REF-{i:03d} --> PRODUTO {i} / UN / 2 / 100,00 / 200,00")
        y -= 0.5*cm
        
        if y < 3*cm and i < 15:
            c.showPage()
            y = height - 2*cm
    
    c.drawString(2*cm, 3*cm, "VALOR A PAGAR R$ 3.000,00")
    c.save()
    print(f"PDF criado: {pdf_path}")

def create_incomplete_pdf():
    """Cria um PDF sem campos obrigatórios."""
    pdf_path = Path(__file__).parent / "pdfs" / "incomplete.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    
    c.setFont("Helvetica", 12)
    y = height - 2*cm
    
    # Faltando número do orçamento e vendedor
    c.drawString(2*cm, y, "Data: 01/01/25")
    y -= 0.7*cm
    
    c.drawString(2*cm, y, "Cliente: EMPRESA SEM PEDIDO")
    y -= 1*cm
    
    c.drawString(2*cm, y, "Sem produtos listados")
    
    c.save()
    print(f"PDF criado: {pdf_path}")

def create_corrupted_pdf():
    """Cria um arquivo PDF corrompido."""
    pdf_path = Path(__file__).parent / "pdfs" / "corrupted.pdf"
    
    # Cria um PDF inválido
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4\n')
        f.write(b'This is not a valid PDF content\n')
        f.write(b'%%EOF')
    
    print(f"PDF corrompido criado: {pdf_path}")

if __name__ == "__main__":
    # Garante que o diretório existe
    pdf_dir = Path(__file__).parent / "pdfs"
    pdf_dir.mkdir(exist_ok=True)
    
    create_sample_order_pdf()
    create_special_chars_pdf()
    create_multipage_pdf()
    create_incomplete_pdf()
    create_corrupted_pdf()
    
    print("Todos os PDFs de teste foram criados!")