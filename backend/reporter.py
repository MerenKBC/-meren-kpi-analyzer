from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
import datetime

class SalesReporter:
    @staticmethod
    def generate_pdf_report(org_name: str, kpis: dict, trends: list, insights: list):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        # Title
        title = Paragraph(f"KPI Pilot Report: {org_name}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        # Date
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        elements.append(Paragraph(f"Generated on: {date_str}", styles['Normal']))
        elements.append(Spacer(1, 24))

        # KPI Summary Table
        elements.append(Paragraph("KPI Summary", styles['Heading2']))
        elements.append(Spacer(1, 12))
        
        data = [
            ["Metric", "Value"],
            ["Total Revenue", f"₺{kpis.get('total_revenue', 0):,.2f}"],
            ["Period", kpis.get('period', 'N/A')],
            ["Total Data Points", str(kpis.get('metric_count', 0))]
        ]
        
        table = Table(data, colWidths=[200, 200])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        elements.append(Spacer(1, 24))

        # Insights Section
        if insights:
            elements.append(Paragraph("AI-Powered Insights", styles['Heading2']))
            elements.append(Spacer(1, 12))
            
            for insight in insights[:5]: # Top 5 insights
                elements.append(Paragraph(f"<b>Explain:</b> {insight.cause_explanation}", styles['Normal']))
                elements.append(Paragraph(f"<i>Impact: {insight.impact_score}</i>", styles['Italic']))
                elements.append(Spacer(1, 12))

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()
