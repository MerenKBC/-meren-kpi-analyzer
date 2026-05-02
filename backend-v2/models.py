from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    tier = Column(String, default="FREE") # FREE, PRO, GROWTH, AGENCY
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    organizations = relationship("Organization", back_populates="owner")

class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String)
    owner_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    owner = relationship("User", back_populates="organizations")
    data_sources = relationship("DataSource", back_populates="organization")
    metrics = relationship("KPIMetric", back_populates="organization")

class DataSource(Base):
    __tablename__ = "data_sources"
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"))
    provider = Column(String) # shopify, ga4, stripe, meta
    credentials = Column(JSON) # OAuth tokens, etc.
    status = Column(String, default="ACTIVE")
    last_sync = Column(DateTime)
    
    organization = relationship("Organization", back_populates="data_sources")

class KPIMetric(Base):
    __tablename__ = "kpi_metrics"
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"))
    name = Column(String) # revenue, conversion_rate, etc.
    value = Column(Float)
    timestamp = Column(DateTime, index=True)
    segment = Column(String, nullable=True) # mobile, desktop, etc.
    source = Column(String, nullable=True) # google, facebook, etc.
    
    organization = relationship("Organization", back_populates="metrics")
    insights = relationship("Insight", back_populates="metric")

class Insight(Base):
    __tablename__ = "insights"
    id = Column(String, primary_key=True, default=generate_uuid)
    metric_id = Column(String, ForeignKey("kpi_metrics.id"))
    cause_explanation = Column(Text)
    action_items = Column(JSON) # List of suggestions
    impact_score = Column(String) # High, Medium, Low
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    metric = relationship("KPIMetric", back_populates="insights")

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(String, primary_key=True, default=generate_uuid)
    organization_id = Column(String, ForeignKey("organizations.id"))
    metric_name = Column(String)
    detected_value = Column(Float)
    expected_value = Column(Float)
    severity = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Integer, default=0)
