from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode
from decimal import Decimal
import os


def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # 🏢 HEADER ENTREPRISE
    p.setFont("Helvetica-Bold", 18)
    p.drawString(200, 800, "AGROMARKET")

    p.setFont("Helvetica", 10)
    p.drawString(200, 785, "Plateforme agricole digitale")

    # 📍 ADRESSE ENTREPRISE
    p.drawString(50, 760, "Adresse: Niamey, Niger")
    p.drawString(50, 745, "Email: contact@agromarket.com")
    p.drawString(50, 730, "Tel: +227 90 00 00 00")

    # 🧾 FACTURE INFO
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, f"FACTURE: {order.invoice_number}")
    p.drawString(50, 685, f"Date: {order.created_at.strftime('%d/%m/%Y')}")

    # 👤 CLIENT
    p.setFont("Helvetica", 11)
    p.drawString(50, 660, f"Client: {order.name}")
    p.drawString(50, 645, f"Téléphone: {order.phone}")
    p.drawString(50, 630, f"Adresse: {order.address}")

    # 📦 TABLE HEADER
    y = 590
    p.setFont("Helvetica-Bold", 10)
    p.drawString(50, y, "Produit")
    p.drawString(250, y, "Qté")
    p.drawString(300, y, "PU")
    p.drawString(380, y, "Total")

    y -= 20
    p.setFont("Helvetica", 10)

    subtotal = Decimal("0")

    for item in order.items.all():

        qty = Decimal(str(item.quantity))
        price = Decimal(str(item.price))

        total_line = price * qty
        subtotal += total_line

        p.drawString(50, y, str(item.product.name))
        p.drawString(250, y, str(item.quantity))
        p.drawString(300, y, f"{price:.2f}")
        p.drawString(380, y, f"{total_line:.2f}")

        y -= 20

    # 💰 TOTALS
    tva = subtotal * Decimal("0.10")
    total = subtotal + tva

    y -= 20
    p.setFont("Helvetica-Bold", 11)
    p.drawString(50, y, f"Sous-total: {subtotal:.2f} FCFA")
    p.drawString(50, y - 15, f"TVA (10%): {tva:.2f} FCFA")
    p.drawString(50, y - 30, f"TOTAL: {total:.2f} FCFA")

    # 🔳 QR CODE
    qr_data = f"https://wa.me/2780607502?text=Commande%20{order.invoice_number}"
    qr = qrcode.make(qr_data)

    qr_path = "/tmp/qr.png"
    qr.save(qr_path)

    p.drawImage(qr_path, 450, 650, width=100, height=100)

    #  SIGNATURE
    p.setFont("Helvetica", 10)
    p.drawString(50, 120, "Signature: Administration AgroMarket")

    # FOOTER LÉGAL
    p.setFont("Helvetica", 8)
    p.drawString(50, 60, "Facture générée automatiquement par AgroMarket.")
    p.drawString(50, 45, "Aucun remboursement sans validation préalable.")

    p.showPage()
    p.save()

    buffer.seek(0)
    return buffer