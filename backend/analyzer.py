import pandas as pd
import numpy as np

class SalesAnalyzer:
    def __init__(self, data_frame):
        self.df = data_frame
        self._prepare_data()

    def _prepare_data(self):
        # Convert date to datetime
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'])
        
        # Ensure numeric columns
        numeric_cols = ['Quantity', 'UnitPrice', 'TotalSale']
        for col in numeric_cols:
            if col in self.df.columns:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce').fillna(0)
        
        # Calculate TotalSale if not present
        if 'TotalSale' not in self.df.columns and 'Quantity' in self.df.columns and 'UnitPrice' in self.df.columns:
            self.df['TotalSale'] = self.df['Quantity'] * self.df['UnitPrice']

    def get_kpis(self):
        total_revenue = self.df['TotalSale'].sum()
        total_orders = len(self.df)
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        total_items = self.df['Quantity'].sum()
        
        return {
            "total_revenue": float(total_revenue),
            "total_orders": int(total_orders),
            "avg_order_value": float(avg_order_value),
            "total_items": int(total_items)
        }

    def get_category_analysis(self):
        if 'Category' not in self.df.columns:
            return {}
        
        category_stats = self.df.groupby('Category')['TotalSale'].sum().sort_values(ascending=False)
        return category_stats.to_dict()

    def get_daily_trend(self):
        if 'Date' not in self.df.columns:
            return {}
        
        daily_stats = self.df.groupby(self.df['Date'].dt.date)['TotalSale'].sum()
        return {str(k): float(v) for k, v in daily_stats.to_dict().items()}
