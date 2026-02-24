import matplotlib.pyplot as plt
import io
import base64

class SalesVisualizer:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        # Set dark theme style
        plt.style.use('dark_background')

    def generate_category_chart(self):
        data = self.analyzer.get_category_analysis()
        if not data:
            return None
        
        plt.figure(figsize=(10, 6))
        plt.bar(data.keys(), data.values(), color='#3b82f6')
        plt.title('Kategori Bazlı Satışlar')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        return self._to_base64()

    def generate_trend_chart(self):
        data = self.analyzer.get_daily_trend()
        if not data:
            return None
            
        plt.figure(figsize=(10, 6))
        plt.plot(list(data.keys()), list(data.values()), marker='o', color='#10b981')
        plt.title('Günlük Satış Trendi')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        return self._to_base64()

    def _to_base64(self):
        buf = io.BytesIO()
        plt.savefig(buf, format='png', transparent=True)
        plt.close()
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

    def save_to_file(self, filename):
        buf = io.BytesIO()
        plt.savefig(filename, format='png')
        plt.close()
