# modules/invoice.py — Generates a PDF invoice for a sale

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
from database import get_sale_with_items


def generate_invoice_pdf(sale_id, shop_name="FertiTrack Fertilizer Shop",
                         shop_address="", shop_phone=""):
    """
    Generates a PDF invoice for the given sale_id.
    Returns the file path of the generated PDF.
    """
    sale, items = get_sale_with_items(sale_id)
    if not sale:
        raise ValueError(f"No sale found with ID {sale_id}")

    os.makedirs("invoices", exist_ok=True)
    file_path = f"invoices/invoice_{sale_id}.pdf"

    doc = SimpleDocTemplate(file_path, pagesize=A4,
                            topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    elements = []

    # Shop header
    title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                 fontSize=18, spaceAfter=4)
    elements.append(Paragraph(shop_name, title_style))
    if shop_address:
        elements.append(Paragraph(shop_address, styles["Normal"]))
    if shop_phone:
        elements.append(Paragraph(f"Phone: {shop_phone}", styles["Normal"]))
    elements.append(Spacer(1, 10*mm))

    # Invoice info
    elements.append(Paragraph(f"<b>Invoice #INV-{sale['sale_id']:04d}</b>",
                              styles["Heading2"]))
    elements.append(Paragraph(f"Date: {str(sale['sale_date'])[:16]}",
                              styles["Normal"]))
    elements.append(Paragraph(f"Customer: {sale['customer_name'] or 'Walk-in Customer'}",
                              styles["Normal"]))
    if sale["customer_phone"]:
        elements.append(Paragraph(f"Phone: {sale['customer_phone']}", styles["Normal"]))
    elements.append(Spacer(1, 8*mm))

    # Items table
    table_data = [["Product", "Qty", "Unit", "Rate (₹)", "Total (₹)"]]
    for item in items:
        table_data.append([
            item["product_name"],
            f"{item['quantity_sold']:.2f}",
            item["unit"],
            f"{item['selling_price']:.2f}",
            f"{item['line_total']:.2f}",
        ])
    

    table = Table(table_data, colWidths=[60*mm, 25*mm, 25*mm, 30*mm, 30*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f6e56")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6*mm))
    from config import SHOP_GSTIN, SHOP_NAME, SHOP_ADDRESS, SHOP_PHONE
    from database import get_gst_summary_for_invoice

# Add this inside generate_invoice_pdf(), after totals_table:

    elements.append(Spacer(1, 6*mm))
    elements.append(Paragraph("<b>GST Breakdown</b>", styles["Heading3"]))

    gst_summary = get_gst_summary_for_invoice(sale_id)
    gst_data = [["HSN", "GST Rate", "Taxable Amount", "CGST", "SGST", "Total GST"]]
    for rate, vals in gst_summary.items():
       total_gst = vals["cgst"] + vals["sgst"]
       gst_data.append([
           vals["hsn"],
           f"{rate}%",
           f"₹{vals['taxable']:.2f}",
           f"₹{vals['cgst']:.2f}",
           f"₹{vals['sgst']:.2f}",
           f"₹{total_gst:.2f}",
        ])

    gst_table = Table(gst_data, colWidths=[25*mm, 20*mm, 35*mm, 25*mm, 25*mm, 25*mm])
    gst_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f6e56")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
     
    ]))
    elements.append(gst_table)
    elements.append(Spacer(1, 4*mm))
    elements.append(Paragraph(f"GSTIN: {SHOP_GSTIN}", styles["Normal"]))

    # Totals
    totals_data = [
        ["Subtotal", f"₹{sale['total_amount']:.2f}"],
        ["Discount", f"₹{sale['discount']:.2f}"],
        ["Total Payable", f"₹{sale['final_amount']:.2f}"],
    ]
    totals_table = Table(totals_data, colWidths=[140*mm, 30*mm])
    totals_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 2), (-1, 2), 12),
        ("LINEABOVE", (0, 2), (-1, 2), 1, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(totals_table)
    elements.append(Spacer(1, 10*mm))

    elements.append(Paragraph(f"Payment Mode: {sale['payment_mode']}  |  "
                              f"Status: {sale['payment_status']}", styles["Normal"]))
    elements.append(Spacer(1, 12*mm))
    elements.append(Paragraph("Thank you for your business!", styles["Italic"]))

    doc.build(elements)
    return file_path