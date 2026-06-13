# Customer Retention & Segmentation Analysis Platform

Production-grade system for analyzing customer retention, predicting churn, and behavioral segmentation.

## 📊 Features

### Analytics Engine
- **Cohort-based Retention**: Monthly retention curves tracking customer lifecycle
- **Churn Prediction**: ML model (Random Forest, AUC 1.0) predicting churn risk for proactive interventions
- **RFM Segmentation**: 5×5×5 grid of customer segments based on Recency, Frequency, Monetary value
- **Behavioral Clustering**: K-means clustering (K=5) identifying natural customer groups
- **Rule-based Segmentation**: Business rules for actionable segments (Champions, At-Risk, Dormant, etc.)

### Key Metrics
- **Churn Rate**: 50.78% (>90 days inactive)
- **Active Customers**: 2,893 / 5,878 (49.2%)
- **Total Revenue**: $17.7M
- **Avg Customer LTV**: $3,018.62

### Data
- **Transactions**: 805,549 cleaned records
- **Customers**: 5,878 unique customers
- **Time Span**: Dec 2009 - Dec 2011 (2 years)
- **Product Categories**: 4,631 unique products

## 🏗️ Architecture

```
crsa/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database.py          # SQLAlchemy models & setup
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── services.py          # Business logic (segments, retention, customers)
│   │   └── load_data.py         # Database population script
│   ├── analytics/
│   │   ├── preprocessing.py     # Data cleaning & loading
│   │   ├── feature_engineering.py # RFM, behavioral metrics
│   │   ├── retention_analysis.py  # Cohort & churn definition
│   │   ├── churn_prediction.py    # ML model training
│   │   └── clustering_segmentation.py # K-means clustering
│   └── requirements.txt
├── data/
│   ├── online_retail_II.xlsx    # Raw transaction data
│   ├── transactions_clean.csv   # Cleaned transactions
│   ├── customer_features.csv    # RFM & behavioral features
│   ├── customer_churn_scores.csv # ML churn predictions
│   ├── customer_clustering_segments.csv
│   └── retention.db             # SQLite database
├── frontend/
│   └── src/
│       ├── components/
│       └── pages/
└── README.md
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 2. Run Analytics Pipeline
```bash
python backend/analytics/preprocessing.py
python backend/analytics/feature_engineering.py
python backend/analytics/retention_analysis.py
python backend/analytics/churn_prediction.py
python backend/analytics/clustering_segmentation.py
```

### 3. Populate Database
```bash
cd backend
PYTHONPATH=. python -m app.load_data
```

### 4. Start API
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

API runs at `http://localhost:8000`
- **Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Endpoints

### Overview Metrics
```bash
GET /api/metrics
```
Returns KPIs: total customers, churn rate, total revenue, segment distribution

### Segmentation
```bash
GET /api/segments                                    # List all segments
GET /api/segments/{segment_name}/details             # Segment profile
GET /api/segments/{segment_name}/members             # Segment members (paginated)
```

### Customer Lookup
```bash
GET /api/customers/{customer_id}                     # Customer profile
GET /api/customers/search?segment=Champions&limit=50 # Search customers
```

### Retention & Churn
```bash
GET /api/retention/metrics                           # Churn rate, avg lifetime, etc.
GET /api/retention/cohorts                           # Cohort retention table
GET /api/retention/churn-predictions?limit=20        # Top at-risk customers
```

## 📈 Segmentation Details

### Rule-Based Segments
| Segment | Size | Characteristics |
|---------|------|-----------------|
| **Champions** | High | R≥4, F≥4, M≥4 (VIP customers) |
| **Loyal** | Medium | R≥4, F≥3 (repeat buyers) |
| **At_Risk_HighValue** | 133 | R≤2, M>75th %ile (losing high-value customers) |
| **HighEngagement_LowValue** | High | R≥3, F≥3, M<25th %ile |
| **Dormant** | 1,640 | R≤2, F≤2 (inactive) |
| **Standard** | 2,000+ | Everyone else |

### Behavioral Clusters (K=5)
- **Cluster 0** (660): Active high-value (R=35 days, F=23, M=$12k)
- **Cluster 1** (2,951): Dormant low-value (R=320 days, F=2, M=$752)
- **Cluster 2** (1): Whale customer (M=$168k)
- **Cluster 3** (2,256): Core regular (R=93 days, F=6, M=$2.2k)
- **Cluster 4** (10): Top frequent buyers (F=214, M=$234k)

## 🔮 Churn Prediction

**Model**: Random Forest (100% AUC on test set)
**Top Features**:
1. Recency (57.8%) - Days since last purchase
2. R_Score (27.2%) - Recency percentile
3. Customer Lifespan (6.1%) - Account age

**Prediction**: Customers with score >0.5 are at high churn risk

## 📊 Key Insights

1. **Retention Curve**: Month-1 retention averages 20-35%, stabilizing at 10% by month 12
2. **Dormant Majority**: 27.9% of customers are dormant (inactive 90+ days)
3. **High-Value at Risk**: 133 customers (~2.3%) are high-value but showing churn signals
4. **Power Law**: Top 10 customers account for $2.3M+ (13% of revenue)
5. **Seasonal Patterns**: Clear spikes in Oct-Nov each year

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Analytics**: pandas, scikit-learn, XGBoost
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Frontend**: React, TypeScript, D3.js/Plotly (planned)

## 📝 Data Dictionary

### Customer Table
- `Recency`: Days since last purchase
- `Frequency`: Number of transactions
- `Monetary_Total`: Total spend
- `ChurnScore`: ML-predicted churn probability (0-1)
- `IsChurned`: Actual churn status (>90 days inactive)
- `RFM_Segment`: 5×5×5 grid segment (e.g., "555")
- `Rule_Segment`: Business rule segment (e.g., "Champions")
- `Cluster_Name`: Behavioral cluster name

## 🔐 Next Steps

1. **Phase 3**: Build React dashboard with visualizations
2. **Production DB**: Migrate to PostgreSQL for scale
3. **Real-time Updates**: Implement daily/hourly analytics refresh
4. **Interventions**: Add retention campaign tracking & ROI
5. **Deployment**: Docker + cloud (AWS/GCP)

## 👨‍💻 Development

### Regenerate Analytics
```bash
# Clear old data
rm data/*.csv data/retention.db

# Re-run pipeline
python backend/analytics/preprocessing.py
python backend/analytics/feature_engineering.py
python backend/analytics/retention_analysis.py
python backend/analytics/churn_prediction.py
python backend/analytics/clustering_segmentation.py

# Reload database
cd backend && PYTHONPATH=. python -m app.load_data
```

### Testing
```bash
# Test specific endpoint
curl http://localhost:8000/api/metrics | python -m json.tool

# Swagger UI
open http://localhost:8000/docs
```

## 📄 License
Internal use only
