import requests
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
import models
import datetime

load_dotenv()

SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = os.getenv("SHOPIFY_API_SECRET")
REDIRECT_URI = os.getenv("SHOPIFY_REDIRECT_URI", "http://localhost:8000/shopify/callback")

class ShopifyManager:
    @staticmethod
    def get_auth_url(shop_name: str):
        # scope: read_products, read_orders, read_content
        scopes = "read_products,read_orders"
        return f"https://{shop_name}.myshopify.com/admin/oauth/authorize?client_id={SHOPIFY_API_KEY}&scope={scopes}&redirect_uri={REDIRECT_URI}"

    @staticmethod
    def get_access_token(shop_name: str, code: str):
        url = f"https://{shop_name}.myshopify.com/admin/oauth/access_token"
        payload = {
            "client_id": SHOPIFY_API_KEY,
            "client_secret": SHOPIFY_API_SECRET,
            "code": code
        }
        response = requests.post(url, json=payload)
        return response.json()

    @staticmethod
    def sync_data(db: Session, org_id: str, access_token: str, shop_url: str):
        """
        Syncs orders and calculates revenue from Shopify Admin API.
        """
        # For MVP, we fetch orders from the last 30 days
        since_date = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
        url = f"https://{shop_url}/admin/api/2024-04/orders.json?status=any&created_at_min={since_date}"
        headers = {"X-Shopify-Access-Token": access_token}
        
        try:
            response = requests.get(url, headers=headers)
            orders = response.json().get('orders', [])
            
            for order in orders:
                # Save each order as a KPI metric entry or aggregate them
                # For simplicity, we'll store aggregate daily revenue
                order_date = datetime.datetime.fromisoformat(order['created_at'].split('T')[0])
                revenue = float(order['total_price'])
                
                # Check if we already have this metric for this day
                metric = db.query(models.KPIMetric).filter(
                    models.KPIMetric.organization_id == org_id,
                    models.KPIMetric.name == "revenue",
                    models.KPIMetric.timestamp == order_date
                ).first()
                
                if metric:
                    metric.value += revenue
                else:
                    new_metric = models.KPIMetric(
                        organization_id=org_id,
                        name="revenue",
                        value=revenue,
                        timestamp=order_date,
                        source="shopify"
                    )
                    db.add(new_metric)
            
            db.commit()
            return True
        except Exception as e:
            print(f"Shopify Sync Error: {e}")
            return False

    @staticmethod
    def mock_sync_data(db: Session, org_id: str):
        """
        Generates mock data for demonstration purposes.
        """
        today = datetime.datetime.utcnow().date()
        for i in range(30):
            date = today - datetime.timedelta(days=i)
            # Create a realistic revenue trend with some random noise
            import random
            base_revenue = 1000 + (random.random() * 500)
            # Add a dip 10 days ago to test anomaly detection later
            if i == 10:
                base_revenue *= 0.5
                
            new_metric = models.KPIMetric(
                organization_id=org_id,
                name="revenue",
                value=base_revenue,
                timestamp=datetime.datetime.combine(date, datetime.time.min),
                source="shopify"
            )
            db.add(new_metric)
        
        db.commit()
        return True
