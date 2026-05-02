from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from auth import get_password_hash, create_access_token, ALGORITHM, SECRET_KEY
from shopify import ShopifyManager
from ai_engine import AIEngine
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from jose import JWTError, jwt
import datetime
import json

load_dotenv()

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="KPI Pilot API", version="2.0")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth Dependency
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# Schemas
class UserCreate(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.get("/")
async def root():
    return {"message": "KPI Pilot API is active", "version": "2.0"}

@app.post("/auth/register", response_model=Token)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create default organization
    new_org = models.Organization(name=f"{user.email}'s Org", owner_id=new_user.id)
    db.add(new_org)
    db.commit()
    
    access_token = create_access_token(data={"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/connect/shopify")
def connect_shopify(shop_name: str, current_user: models.User = Depends(get_current_user)):
    auth_url = ShopifyManager.get_auth_url(shop_name)
    return {"auth_url": auth_url}

@app.post("/connect/shopify/mock")
def mock_connect_shopify(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.owner_id == current_user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    new_ds = models.DataSource(
        organization_id=org.id,
        provider="shopify",
        credentials={"access_token": "mock-token", "shop_url": "mock-store.myshopify.com"},
        last_sync=datetime.datetime.utcnow()
    )
    db.add(new_ds)
    db.commit()
    
    ShopifyManager.mock_sync_data(db, org.id)
    return {"message": "Mock Shopify store connected and data synced."}

@app.get("/anomalies")
def get_anomalies(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.owner_id == current_user.id).first()
    if not org:
        return []
    
    metrics = db.query(models.KPIMetric).filter(
        models.KPIMetric.organization_id == org.id
    ).order_by(models.KPIMetric.timestamp.desc()).limit(100).all()
    
    anomalies = AIEngine.detect_anomalies(metrics)
    return anomalies

@app.post("/ai/explain")
def explain_kpi(metric_name: str, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.owner_id == current_user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    metrics = db.query(models.KPIMetric).filter(
        models.KPIMetric.organization_id == org.id,
        models.KPIMetric.name == metric_name
    ).order_by(models.KPIMetric.timestamp.desc()).limit(2).all()
    
    if len(metrics) < 2:
        raise HTTPException(status_code=400, detail="Not enough data to explain trend")
    
    current_val = metrics[0].value
    previous_val = metrics[1].value
    
    insight_data = AIEngine.generate_insight(metric_name, current_val, previous_val)
    
    new_insight = models.Insight(
        metric_id=metrics[0].id,
        cause_explanation=insight_data["explanation"],
        action_items=insight_data["actions"],
        impact_score=insight_data["impact_score"]
    )
    db.add(new_insight)
    db.commit()
    
    return insight_data

from reporter import SalesReporter
from fastapi.responses import Response

# ... (other endpoints)

@app.get("/reports/export")
def export_report(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    org = db.query(models.Organization).filter(models.Organization.owner_id == current_user.id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Gather data for report
    summary = get_summary(current_user, db)
    
    # Fetch recent insights
    insights = db.query(models.Insight).join(models.KPIMetric).filter(
        models.KPIMetric.organization_id == org.id
    ).order_by(models.Insight.created_at.desc()).limit(5).all()
    
    pdf_content = SalesReporter.generate_pdf_report(
        org.name, 
        summary["kpis"], 
        summary["trends"], 
        insights
    )
    
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=kpi_pilot_report_{org.name}.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
