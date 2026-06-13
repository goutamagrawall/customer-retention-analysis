import pandas as pd
from datetime import datetime
from app.database import SessionLocal, init_db
from app.database import Customer, Segment, CohortRetention
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_path = Path(__file__).parent.parent.parent

def load_customer_data():
    init_db()
    db = SessionLocal()

    try:
        logger.info("Loading customer features...")
        features = pd.read_csv(base_path / 'data' / 'customer_features.csv')
        churn_scores = pd.read_csv(base_path / 'data' / 'customer_churn_scores.csv')
        clustering = pd.read_csv(base_path / 'data' / 'customer_clustering_segments.csv')

        df = features.merge(churn_scores, on='Customer ID', how='left')
        df = df.merge(clustering, on='Customer ID', how='left')

        df['FirstPurchaseDate'] = pd.to_datetime(df['FirstPurchaseDate'], errors='coerce')
        df['LastPurchaseDate'] = pd.to_datetime(df['LastPurchaseDate'], errors='coerce')

        logger.info(f"Loading {len(df)} customers into database...")

        for idx, row in df.iterrows():
            customer = Customer(
                customer_id=int(row['Customer ID']),
                recency=float(row['Recency']),
                frequency=int(row['Frequency']),
                monetary_total=float(row['Monetary_Total']),
                monetary_avg=float(row['Monetary_Avg']),
                monetary_std=float(row['Monetary_Std']),
                transaction_count=int(row['Transaction_Count']),
                customer_lifespan_days=int(row['CustomerLifespan_Days']),
                unique_prod_categories=int(row['UniqueProdCategories']),
                max_transaction_amount=float(row['MaxTransactionAmount']),
                avg_days_between_purchases=float(row['AvgDaysBetweenPurchases']),
                r_score=int(row['R_Score']),
                f_score=int(row['F_Score']),
                m_score=int(row['M_Score']),
                rfm_segment=str(row['RFM_Segment']),
                rule_segment=str(row['Rule_Segment']),
                cluster_id=int(row['Cluster']) if 'Cluster' in row else 0,
                cluster_name=str(row['Cluster_Name']) if 'Cluster_Name' in row else 'Unknown',
                churn_score=float(row['ChurnScore']),
                is_churned=bool(row['IsChurned']),
                first_purchase_date=row['FirstPurchaseDate'],
                last_purchase_date=row['LastPurchaseDate'],
                country=str(row['Country']) if 'Country' in row else None
            )
            db.add(customer)

            if (idx + 1) % 500 == 0:
                logger.info(f"Loaded {idx + 1} customers...")

        db.commit()
        logger.info(f"Successfully loaded {len(df)} customers!")

    except Exception as e:
        logger.error(f"Error loading customers: {e}")
        db.rollback()
    finally:
        db.close()

def load_segments():
    db = SessionLocal()

    try:
        logger.info("Loading segments...")

        segment_configs = [
            ("Champions", "rule_based", "Highest-value loyal customers"),
            ("At_Risk_HighValue", "rule_based", "High-value customers at risk of churn"),
            ("Dormant", "rule_based", "Inactive customers"),
            ("Loyal", "rule_based", "Loyal repeat customers"),
            ("HighEngagement_LowValue", "rule_based", "Highly engaged but low monetary value"),
            ("Standard", "rule_based", "Standard customers"),
        ]

        for seg_name, seg_type, description in segment_configs:
            existing = db.query(Segment).filter(Segment.segment_name == seg_name).first()
            if not existing:
                segment = Segment(
                    segment_name=seg_name,
                    segment_type=seg_type,
                    description=description,
                    customer_count=0,
                    avg_recency=0.0,
                    avg_frequency=0.0,
                    avg_monetary=0.0,
                    avg_churn_score=0.0
                )
                db.add(segment)

        db.commit()
        logger.info("Segments loaded!")

    except Exception as e:
        logger.error(f"Error loading segments: {e}")
        db.rollback()
    finally:
        db.close()

def load_cohort_retention():
    db = SessionLocal()

    try:
        logger.info("Loading cohort retention data...")
        cohort_rates = pd.read_csv(base_path / 'data' / 'cohort_retention_table.csv', index_col=0)
        cohort_counts = pd.read_csv(base_path / 'data' / 'cohort_retention_pivot.csv', index_col=0)

        for cohort_month in cohort_rates.index:
            cohort_size = cohort_counts.loc[cohort_month, '0']

            for cohort_age_str in cohort_rates.columns:
                cohort_age = int(cohort_age_str)
                retention_rate = cohort_rates.loc[cohort_month, cohort_age_str]

                if pd.isna(retention_rate):
                    continue

                retained_customers = int(cohort_counts.loc[cohort_month, cohort_age_str])

                cohort_record = CohortRetention(
                    cohort_month=str(cohort_month),
                    cohort_age_months=int(cohort_age),
                    retained_customers=int(retained_customers),
                    cohort_size=int(cohort_size),
                    retention_rate=float(retention_rate)
                )
                db.add(cohort_record)

        db.commit()
        logger.info("Cohort retention data loaded!")

    except Exception as e:
        logger.error(f"Error loading cohort retention: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_customer_data()
    load_segments()
    load_cohort_retention()
    logger.info("Database initialization complete!")
