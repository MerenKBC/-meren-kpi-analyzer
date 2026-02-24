from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import os

class SalesReporter:
    def __init__(self, analyzer, visualizer):
        self.analyzer = analyzer
        self.visualizer = visualizer
        self.styles = getSampleStyleSheet()

    def generate_pdf(self):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        # Title
        title_style = ParagraphStyle(
            'TitleStyle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.hexColor("#333333"),
            spaceAfter=30
        )
        elements.append(Paragraph("Satış Analiz Raporu", title_style))
        elements.append(Spacer(1, 12))

        # KPI Section
        kpis = self.analyzer.get_kpis()
        elements.append(Paragraph("Temel Performans Göstergeleri (KPI)", self.styles['Heading2']))
        
        kpi_data = [
            ["Metrik", "Değer"],
            ["Toplam Gelir", f"₺{kpis['total_revenue']:,.2f}"],
            ["Toplam Sipariş", kpis['total_orders']],
            ["Ort. Sipariş Değeri", f"₺{kpis['avg_order_value']:,.2f}"],
            ["Toplam Ürün Satışı", kpis['total_items']]
        ]
        
        t = Table(kpi_data, colWidths=[200, 200])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1, 30))

        # Charts
        # We need to save visualizer charts to temporary files because ReportLab Image needs a file/path or file-like object
        # but the visualizer currently returns base64. Let's add a helper to save or use BytesIO.
        
        # Trend Chart
        elements.append(Paragraph("Satış Trendi", self.styles['Heading2']))
        trend_buf = io.BytesIO()
        self.visualizer.save_trend_to_buf(trend_buf)
        trend_buf.seek(0)
        if trend_buf.getbuffer().nbytes > 0:
            elements.append(Image(trend_buf, width=400, height=250))
        elements.append(Spacer(1, 30))

        # Category Chart
        elements.append(Paragraph("Kategori Analizi", self.styles['Heading2']))
        cat_buf = io.BytesIO()
        self.visualizer.save_category_to_buf(cat_buf)
        cat_buf.seek(0)
        if cat_buf.getbuffer().nbytes > 0:
            elements.append(Image(cat_buf, width=400, height=250))

        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
