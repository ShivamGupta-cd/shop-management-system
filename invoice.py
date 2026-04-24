def generate_invoice(
    sale_id,
    buyer_name="",
    buyer_address="",
    buyer_phone="",
    gst_percent=0,
    do_print=True,
    cart=None
):
    import os
    import subprocess
    from datetime import datetime
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A5
    from reportlab.lib.styles import getSampleStyleSheet
    from database import connect

    # ---------------- SAVE LOCATION ----------------
    base_dir = os.path.join(os.path.expanduser("~"), "Documents", "shop")
    invoice_dir = os.path.join(base_dir, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"invoice_{sale_id}.pdf")

    # ---------------- DOCUMENT ----------------
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A5,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()
    elements = []

    # ---------------- HEADER ----------------
    elements.append(Paragraph("<b>GIRIRAJ TRADERS</b>", styles['Title']))
    elements.append(Paragraph("Phone No. - 9810241824", styles['Normal']))
    elements.append(Spacer(1, 8))

    # ---------------- DATE ----------------
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("SELECT date FROM sales WHERE id=?", (sale_id,))
    result = cursor.fetchone()
    conn.close()

    date = result[0] if result else datetime.now().strftime("%Y-%m-%d")

    elements.append(Paragraph("<b>ESTIMATE</b>", styles['Title']))
    elements.append(Paragraph(f"Date: {date}", styles['Normal']))
    elements.append(Spacer(1, 8))

    # ---------------- BUYER ----------------
    elements.append(Paragraph("<b>Buyer Details:</b>", styles['Normal']))
    elements.append(Paragraph(f"Name: {buyer_name or '-'}", styles['Normal']))
    elements.append(Paragraph(f"Address: {buyer_address or '-'}", styles['Normal']))
    elements.append(Paragraph(f"Phone: {buyer_phone or '-'}", styles['Normal']))
    elements.append(Spacer(1, 10))

    # ---------------- TABLE ----------------
    data = [["Item", "Qty", "MRP", "Rate", "Amt"]]

    subtotal = 0

    if cart:
        for item in cart.values():
            name = item["name"].title()
            qty = item["qty"]
            rate = item["price"]
            discount = item.get("discount", 0)
            mrp = item.get("mrp", 0)

            amount = (qty * rate) - discount
            subtotal += amount

            data.append([
                name,
                str(qty),
                f"{mrp:.2f}" if mrp else "-",
                f"{rate:.2f}",
                f"{amount:.2f}"
            ])

    table = Table(data, colWidths=[100, 30, 40, 40, 50])

    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.8, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 10))

    # ---------------- GST ----------------
    try:
        gst_percent = float(gst_percent)
    except:
        gst_percent = 0

    cgst_rate = gst_percent / 2
    sgst_rate = gst_percent / 2

    cgst_amt = subtotal * cgst_rate / 100
    sgst_amt = subtotal * sgst_rate / 100

    grand_total = subtotal + cgst_amt + sgst_amt

    # ---------------- TOTAL ----------------
    elements.append(Paragraph(f"Subtotal: {subtotal:.2f}", styles['Normal']))
    elements.append(Paragraph(f"CGST ({cgst_rate}%): {cgst_amt:.2f}", styles['Normal']))
    elements.append(Paragraph(f"SGST ({sgst_rate}%): {sgst_amt:.2f}", styles['Normal']))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(f"<b>Grand Total: {grand_total:.2f}</b>", styles['Normal']))

    # ---------------- FOOTER ----------------
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Authorized Signature", styles['Normal']))

    # ---------------- BUILD ----------------
    doc.build(elements)

    print("Invoice Created:", file_path)

    # ---------------- PRINT ----------------
    if do_print:
        try:
            sumatra_path = os.path.join(
                os.path.expanduser("~"),
                "AppData", "Local", "SumatraPDF", "SumatraPDF.exe"
            )

            if os.path.exists(sumatra_path):
                subprocess.Popen([
                    sumatra_path,
                    "-print-to-default",
                    file_path
                ], shell=True)
            else:
                # fallback → just open PDF
                os.startfile(file_path)

        except Exception as e:
            print("Print failed:", e)