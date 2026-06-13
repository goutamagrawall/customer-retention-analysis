from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import init_db, get_db
from app.services import SegmentService, RetentionService, CustomerService
from app.schemas import (
    CustomerDetail, SegmentProfile, CohortRetentionRow,
    ChurnRiskCustomer, OverviewMetrics, APIResponse
)
from typing import List

app = FastAPI(
    title="Customer Retention & Segmentation API",
    description="Industry-grade API for customer analytics",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "retention-api"}

@app.get("/api/metrics", response_model=OverviewMetrics)
def get_overview_metrics(db: Session = Depends(get_db)):
    return CustomerService.get_overview_metrics(db)

@app.get("/api/segments", response_model=List[SegmentProfile])
def list_segments(db: Session = Depends(get_db)):
    return SegmentService.get_all_segments(db)

@app.get("/api/segments/{segment_name}/details")
def get_segment_details(segment_name: str, db: Session = Depends(get_db)):
    details = SegmentService.get_segment_details(db, segment_name)
    if not details:
        raise HTTPException(status_code=404, detail="Segment not found")
    return details

@app.get("/api/segments/{segment_name}/members", response_model=List[CustomerDetail])
def get_segment_members(
    segment_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return SegmentService.get_segment_members(db, segment_name, skip, limit)

@app.get("/api/customers/search", response_model=List[CustomerDetail])
def search_customers(
    segment: str = Query(None),
    min_churn_score: float = Query(None, ge=0, le=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return CustomerService.search_customers(db, segment, min_churn_score, skip, limit)

@app.get("/api/customers/{customer_id}", response_model=CustomerDetail)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = CustomerService.get_customer_by_id(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.get("/api/retention/cohorts")
def get_cohort_retention(db: Session = Depends(get_db)):
    return RetentionService.get_cohort_retention(db)

@app.get("/api/retention/churn-predictions", response_model=List[ChurnRiskCustomer])
def get_churn_predictions(
    limit: int = Query(20, ge=1, le=500),
    db: Session = Depends(get_db)
):
    return RetentionService.get_churn_prediction_top_n(db, limit)

@app.get("/api/retention/metrics")
def get_retention_metrics(db: Session = Depends(get_db)):
    return RetentionService.get_retention_metrics(db)

import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve React static frontend
dist_path = os.path.join(os.path.dirname(__file__), "..", "dist")
if os.path.exists(dist_path):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")

    @app.get("/{fallback_path:path}")
    def serve_frontend(fallback_path: str):
        return FileResponse(os.path.join(dist_path, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
