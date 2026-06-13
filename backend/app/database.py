from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pathlib import Path
import os

db_path = Path(__file__).parent.parent.parent / "data" / "retention.db"
# Fallback for container environment where project root is /app
if not db_path.exists() and Path("/app/data/retention.db").exists():
    db_path = Path("/app/data/retention.db")

DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    DATABASE_URL,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    recency = Column(Float)
    frequency = Column(Integer)
    monetary_total = Column(Float)
    monetary_avg = Column(Float)
    monetary_std = Column(Float)
    transaction_count = Column(Integer)
    customer_lifespan_days = Column(Integer)
    unique_prod_categories = Column(Integer)
    max_transaction_amount = Column(Float)
    avg_days_between_purchases = Column(Float)
    r_score = Column(Integer)
    f_score = Column(Integer)
    m_score = Column(Integer)
    rfm_segment = Column(String)
    rule_segment = Column(String)
    cluster_id = Column(Integer)
    cluster_name = Column(String)
    churn_score = Column(Float)
    is_churned = Column(Boolean)
    first_purchase_date = Column(DateTime)
    last_purchase_date = Column(DateTime)
    country = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Segment(Base):
    __tablename__ = "segments"

    segment_id = Column(Integer, primary_key=True, index=True)
    segment_name = Column(String, unique=True)
    segment_type = Column(String)
    description = Column(Text)
    customer_count = Column(Integer)
    avg_recency = Column(Float)
    avg_frequency = Column(Float)
    avg_monetary = Column(Float)
    avg_churn_score = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

class CohortRetention(Base):
    __tablename__ = "cohort_retention"

    cohort_id = Column(Integer, primary_key=True, index=True)
    cohort_month = Column(String)
    cohort_age_months = Column(Integer)
    retained_customers = Column(Integer)
    cohort_size = Column(Integer)
    retention_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class MetricSnapshot(Base):
    __tablename__ = "metric_snapshots"

    metric_id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String)
    metric_value = Column(Float)
    snapshot_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
