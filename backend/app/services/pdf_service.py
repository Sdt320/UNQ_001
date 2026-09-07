"""Dynamic PDF Invoice generator using ReportLab."""

import io
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from app.core.logging import logger


class PDFInvoiceService:
    @staticmethod
    def generate_invoice_pdf(
        job_id: str,
        customer_name: str,
        officer_name: str,
        category: str,
        labor_cost: float = 85.00,
        materials_cost: float = 17.00,
        platform_fee: float = 18.00,
        output_filepath: Optional[str] = None
    ) -> bytes:
        """
        Generates an itemized official PDF invoice.
        """
        total_amount = labor_cost + materials_cost + platform_fee
        technician_payout = round(total_amount * 0.85, 2)

        buffer = io.BytesIO()

        if REPORTLAB_AVAILABLE:
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor("#1e293b"),
                spaceAfter=12
            )
            subtitle_style = ParagraphStyle(
                'DocSub',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor("#64748b")
            )
            heading_style = ParagraphStyle(
                'SectionHead',
                parent=styles['Heading2'],
                fontSize=12,
                leading=16,
                textColor=colors.HexColor("#0f172a"),
                spaceBefore=12,
                spaceAfter=6
            )

            elements = []

            # Brand Header
            elements.append(Paragraph("<b>FIELDMIND AI</b> — Official Service Invoice", title_style))
            elements.append(Paragraph(f"Autonomous Field Operations Network | Invoice Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", subtitle_style))
            elements.append(Spacer(1, 15))

            # Meta Info Table
            meta_data = [
                [Paragraph("<b>Job Reference ID:</b>", subtitle_style), Paragraph(str(job_id), subtitle_style)],
                [Paragraph("<b>Customer Name:</b>", subtitle_style), Paragraph(str(customer_name), subtitle_style)],
                [Paragraph("<b>Certified Technician:</b>", subtitle_style), Paragraph(str(officer_name), subtitle_style)],
                [Paragraph("<b>Trade Category:</b>", subtitle_style), Paragraph(str(category), subtitle_style)],
                [Paragraph("<b>Payment Status:</b>", subtitle_style), Paragraph("<font color='green'><b>PAID & SETTLED (ESCROW)</b></font>", subtitle_style)],
            ]
            t_meta = Table(meta_data, colWidths=[150, 350])
            t_meta.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
                ('TOPPADDING', (0,0), (-1,-1), 4),
                ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ]))
            elements.append(t_meta)
            elements.append(Spacer(1, 15))

            # Itemized Costs Table
            elements.append(Paragraph("<b>Itemized Repair Breakdown</b>", heading_style))
            items_data = [
                ["Description", "Classification", "Amount (USD)"],
                [f"Certified {category} On-Site Diagnostic & Labor", "Labor", f"${labor_cost:.2f}"],
                ["Approved Replacement Parts & Seal Materials", "Materials", f"${materials_cost:.2f}"],
                ["Autonomous Dispatch & Escrow Insurance Fee (15%)", "Platform Fee", f"${platform_fee:.2f}"],
                ["", "TOTAL AMOUNT", f"${total_amount:.2f}"]
            ]
            t_items = Table(items_data, colWidths=[260, 140, 100])
            t_items.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (2,0), (2,-1), 'RIGHT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (0,1), (-1,-2), colors.white),
                ('GRID', (0,0), (-1,-2), 0.5, colors.HexColor("#cbd5e1")),
                ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor("#f1f5f9")),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('LINEABOVE', (0,-1), (-1,-1), 1.5, colors.HexColor("#0f172a")),
                ('TOPPADDING', (0,-1), (-1,-1), 6),
                ('BOTTOMPADDING', (0,-1), (-1,-1), 6),
            ]))
            elements.append(t_items)
            elements.append(Spacer(1, 15))

            # Escrow Settlement Split Summary
            elements.append(Paragraph("<b>Escrow Split Summary (85/15)</b>", heading_style))
            split_data = [
                ["Field Officer Payout (85%):", f"${technician_payout:.2f}"],
                ["Platform Network Fee (15%):", f"${platform_fee:.2f}"]
            ]
            t_split = Table(split_data, colWidths=[250, 250])
            t_split.setStyle(TableStyle([
                ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#475569")),
                ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Oblique'),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            elements.append(t_split)
            elements.append(Spacer(1, 20))

            elements.append(Paragraph("Thank you for using FieldMind AI. All repairs backed by our 30-day quality guarantee.", subtitle_style))

            doc.build(elements)
            pdf_data = buffer.getvalue()
        else:
            # Fallback simple formatted text PDF mock
            pdf_data = (
                f"%PDF-1.4\nFieldMind AI Invoice\nJob: {job_id}\nCustomer: {customer_name}\n"
                f"Officer: {officer_name}\nCategory: {category}\nTotal: ${total_amount:.2f}\n"
                f"Technician (85%): ${technician_payout:.2f}\nPlatform (15%): ${platform_fee:.2f}\n%%EOF"
            ).encode("utf-8")

        if output_filepath:
            os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
            with open(output_filepath, "wb") as f:
                f.write(pdf_data)

        return pdf_data


pdf_service = PDFInvoiceService()
