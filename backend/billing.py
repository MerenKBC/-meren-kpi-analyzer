import stripe
import os
from dotenv import load_dotenv

load_dotenv()

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class BillingManager:
    @staticmethod
    def create_checkout_session(customer_email: str, price_id: str):
        """
        Creates a Stripe Checkout Session for subscription.
        """
        try:
            checkout_session = stripe.checkout.Session.create(
                line_items=[
                    {
                        'price': price_id,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + '/dashboard?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=os.getenv("FRONTEND_URL", "http://localhost:3000") + '/pricing',
                customer_email=customer_email
            )
            return checkout_session.url
        except Exception as e:
            print(f"Stripe Error: {e}")
            return None

    @staticmethod
    def get_subscription_status(customer_email: str):
        """
        Check if user has an active subscription.
        """
        # In a real app, you'd store the stripe_customer_id in your User model
        # and query Stripe or your own DB.
        return "PRO" # Mocked for MVP
