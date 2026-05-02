import google.generativeai as genai
import os
from dotenv import load_dotenv
import numpy as np
from sqlalchemy.orm import Session
import models
import json

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

class AIEngine:
    @staticmethod
    def detect_anomalies(data_points: list):
        """
        Uses Z-score to detect anomalies in a list of values.
        Returns indices of anomalies.
        """
        if len(data_points) < 7:
            return []
            
        values = [p.value for p in data_points]
        mean = np.mean(values)
        std = np.std(values)
        
        if std == 0:
            return []
            
        anomalies = []
        for i, val in enumerate(values):
            z_score = (val - mean) / std
            if abs(z_score) > 2: # Threshold for anomaly
                anomalies.append({
                    "index": i,
                    "value": val,
                    "expected": mean,
                    "z_score": z_score
                })
        return anomalies

    @staticmethod
    def generate_insight(metric_name: str, current_val: float, previous_val: float, context: dict = None):
        """
        Generates an AI explanation and action suggestions.
        """
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        change_pct = ((current_val - previous_val) / previous_val) * 100 if previous_val != 0 else 0
        status = "increased" if change_pct > 0 else "decreased"
        
        prompt = f"""
        Role: Senior E-commerce Growth Expert
        Event: The metric '{metric_name}' has {status} by {abs(change_pct):.2f}%.
        Current Value: {current_val}
        Previous Value: {previous_val}
        Context: {json.dumps(context) if context else 'No additional context provided.'}
        
        Task:
        1. Explain the potential reasons for this change in 2-3 concise sentences.
        2. Provide 3 specific, actionable recommendations to improve or sustain this performance.
        3. Assign an 'Impact Score' (High, Medium, Low).
        
        Output format (JSON):
        {{
            "explanation": "...",
            "actions": ["action 1", "action 2", "action 3"],
            "impact_score": "..."
        }}
        """
        
        try:
            response = model.generate_content(prompt)
            # Clean response text if it contains markdown code blocks
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
        except Exception as e:
            print(f"AI Generation Error: {e}")
            return {
                "explanation": f"We detected a {abs(change_pct):.2f}% {status} in {metric_name}.",
                "actions": ["Monitor the trend for 48 hours", "Check for site speed issues", "Verify ad campaign tracking"],
                "impact_score": "Medium"
            }
