from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class CustomerBase(BaseModel):
    customer_id: int
    recency: float
    frequency: int
    monetary_total: float
    churn_score: float
    is_churned: bool
    rfm_segment: str
    rule_segment: str
    cluster_name: str

class CustomerDetail(CustomerBase):
    monetary_avg: float
    transaction_count: int
    customer_lifespan_days: int
    unique_prod_categories: int
    max_transaction_amount: float
    r_score: int
    f_score: int
    m_score: int
    first_purchase_date: Optional[datetime]
    last_purchase_date: Optional[datetime]
    country: Optional[str]

    class Config:
        from_attributes = True

class SegmentProfile(BaseModel):
    segment_id: Optional[int]
    segment_name: str
    segment_type: str
    customer_count: int
    avg_recency: float
    avg_frequency: float
    avg_monetary: float
    avg_churn_score: float
    description: Optional[str]

    class Config:
        from_attributes = True

class CohortRetentionRow(BaseModel):
    cohort_month: str
    cohort_age_months: int
    retention_rate: float
    retained_customers: int
    cohort_size: int

class RetentionMetrics(BaseModel):
    churn_rate: float
    avg_customer_lifetime: float
    avg_monetary_value: float
    total_customers: int
    active_customers_last_30_days: int

class ChurnRiskCustomer(BaseModel):
    customer_id: int
    churn_score: float
    recency: int
    frequency: int
    monetary_total: float
    rule_segment: str

class SegmentDistribution(BaseModel):
    segment: str
    count: int
    percentage: float

class OverviewMetrics(BaseModel):
    total_customers: int
    active_customers: int
    churned_customers: int
    churn_rate: float
    total_revenue: float
    avg_customer_ltv: float
    segments: List[SegmentDistribution]

class APIResponse(BaseModel):
    success: bool
    data: Optional[dict]
    message: Optional[str]

class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 50
