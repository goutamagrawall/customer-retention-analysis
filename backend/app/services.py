from sqlalchemy.orm import Session
from app.database import Customer, Segment, CohortRetention
from sqlalchemy import func

class SegmentService:
    @staticmethod
    def get_all_segments(db: Session):
        segments = db.query(Segment).all()
        return segments

    @staticmethod
    def get_segment_by_name(db: Session, segment_name: str):
        segment = db.query(Segment).filter(
            Segment.segment_name == segment_name
        ).first()
        return segment

    @staticmethod
    def get_segment_details(db: Session, segment_name: str):
        customers = db.query(Customer).filter(
            (Customer.rfm_segment == segment_name) |
            (Customer.rule_segment == segment_name) |
            (Customer.cluster_name == segment_name)
        ).all()

        if customers:
            profile = {
                "segment_name": segment_name,
                "customer_count": len(customers),
                "avg_recency": sum(c.recency for c in customers) / len(customers),
                "avg_frequency": sum(c.frequency for c in customers) / len(customers),
                "avg_monetary": sum(c.monetary_total for c in customers) / len(customers),
                "avg_churn_score": sum(c.churn_score for c in customers) / len(customers),
                "churn_percentage": sum(1 for c in customers if c.is_churned) / len(customers) * 100,
            }
            return profile
        return None

    @staticmethod
    def get_segment_members(db: Session, segment_name: str, skip: int = 0, limit: int = 50):
        customers = db.query(Customer).filter(
            (Customer.rfm_segment == segment_name) |
            (Customer.rule_segment == segment_name) |
            (Customer.cluster_name == segment_name)
        ).offset(skip).limit(limit).all()

        return customers

class RetentionService:
    @staticmethod
    def get_cohort_retention(db: Session):
        cohorts = db.query(CohortRetention).order_by(CohortRetention.cohort_month).all()
        cohort_dict = {}

        for cohort in cohorts:
            if cohort.cohort_month not in cohort_dict:
                cohort_dict[cohort.cohort_month] = {}
            cohort_dict[cohort.cohort_month][cohort.cohort_age_months] = {
                "retention_rate": cohort.retention_rate,
                "retained_customers": cohort.retained_customers,
                "cohort_size": cohort.cohort_size
            }

        return cohort_dict

    @staticmethod
    def get_churn_prediction_top_n(db: Session, n: int = 20):
        at_risk = db.query(Customer).filter(
            Customer.churn_score > 0.5
        ).order_by(Customer.churn_score.desc()).limit(n).all()

        return at_risk

    @staticmethod
    def get_retention_metrics(db: Session):
        total_customers = db.query(func.count(Customer.customer_id)).scalar()
        churned_customers = db.query(func.count(Customer.customer_id)).filter(
            Customer.is_churned == True
        ).scalar()
        active_customers = total_customers - churned_customers

        avg_lifetime = db.query(func.avg(Customer.customer_lifespan_days)).scalar() or 0
        avg_monetary = db.query(func.avg(Customer.monetary_total)).scalar() or 0

        churn_rate = (churned_customers / total_customers) if total_customers > 0 else 0

        return {
            "total_customers": total_customers or 0,
            "active_customers": active_customers or 0,
            "churned_customers": churned_customers or 0,
            "churn_rate": churn_rate,
            "avg_customer_lifetime": avg_lifetime,
            "avg_monetary_value": avg_monetary
        }

class CustomerService:
    @staticmethod
    def get_customer_by_id(db: Session, customer_id: int):
        customer = db.query(Customer).filter(
            Customer.customer_id == customer_id
        ).first()
        return customer

    @staticmethod
    def search_customers(db: Session, segment: str = None, min_churn_score: float = None,
                        skip: int = 0, limit: int = 50):
        query = db.query(Customer)

        if segment:
            query = query.filter(
                (Customer.rfm_segment == segment) |
                (Customer.rule_segment == segment) |
                (Customer.cluster_name == segment)
            )

        if min_churn_score is not None:
            query = query.filter(Customer.churn_score >= min_churn_score)

        customers = query.offset(skip).limit(limit).all()

        return customers

    @staticmethod
    def get_overview_metrics(db: Session):
        total_customers = db.query(func.count(Customer.customer_id)).scalar() or 0
        churned_customers = db.query(func.count(Customer.customer_id)).filter(
            Customer.is_churned == True
        ).scalar() or 0
        active_customers = total_customers - churned_customers

        churn_rate = (churned_customers / total_customers) if total_customers > 0 else 0
        total_revenue = db.query(func.sum(Customer.monetary_total)).scalar() or 0
        avg_ltv = (total_revenue / total_customers) if total_customers > 0 else 0

        rule_segments = db.query(
            Customer.rule_segment,
            func.count(Customer.customer_id)
        ).group_by(Customer.rule_segment).all()

        segments_distribution = [
            {
                "segment": seg,
                "count": count,
                "percentage": (count / total_customers * 100) if total_customers > 0 else 0
            }
            for seg, count in rule_segments
        ]

        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "churned_customers": churned_customers,
            "churn_rate": churn_rate,
            "total_revenue": total_revenue,
            "avg_customer_ltv": avg_ltv,
            "segments": segments_distribution
        }
