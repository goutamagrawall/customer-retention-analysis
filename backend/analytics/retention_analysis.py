import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RetentionAnalysis:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.df['InvoiceDate'] = pd.to_datetime(self.df['InvoiceDate'])
        self.df['YearMonth'] = self.df['InvoiceDate'].dt.to_period('M')

    def calculate_cohort_retention(self):
        df = self.df.copy()

        user_first_month = df.groupby('Customer ID')['YearMonth'].min().reset_index()
        user_first_month.columns = ['Customer ID', 'CohortMonth']

        df = df.merge(user_first_month, on='Customer ID', how='left')
        df['CohortAge'] = (df['YearMonth'] - df['CohortMonth']).apply(lambda x: x.n)

        cohort_data = df.groupby(['CohortMonth', 'CohortAge'])['Customer ID'].nunique().reset_index()
        cohort_data.columns = ['CohortMonth', 'CohortAge', 'RetainedUsers']

        cohort_pivot = cohort_data.pivot(index='CohortMonth', columns='CohortAge', values='RetainedUsers')

        cohort_size = cohort_pivot.iloc[:, 0]
        retention_table = cohort_pivot.divide(cohort_size, axis=0)

        logger.info(f"Cohort retention table shape: {retention_table.shape}")
        logger.info(f"\nCohort Retention (first 10 months):\n{retention_table.iloc[:10, :8]}")

        return retention_table, cohort_pivot

    def calculate_churn_definition(self, inactivity_days: int = None):
        df = self.df.copy()
        max_date = df['InvoiceDate'].max()
        customers = df['Customer ID'].unique()

        if inactivity_days is None:
            recent_customers = df[df['InvoiceDate'] >= max_date - timedelta(days=365)]
            df_recent = recent_customers.copy()
            df_recent['DaysSinceLastPurchase'] = (max_date - df_recent.groupby('Customer ID')['InvoiceDate'].transform('max')).dt.days

            churn_candidates = df_recent[df_recent['DaysSinceLastPurchase'] > 60].groupby('Customer ID').size().reset_index(name='count')
            inactivity_days = 90
            logger.info(f"Estimated churn window: {inactivity_days} days")
        else:
            logger.info(f"Using churn window: {inactivity_days} days")

        customer_last_purchase = df.groupby('Customer ID')['InvoiceDate'].max().reset_index()
        customer_last_purchase.columns = ['Customer ID', 'LastPurchaseDate']
        customer_last_purchase['DaysSinceLastPurchase'] = (max_date - customer_last_purchase['LastPurchaseDate']).dt.days
        customer_last_purchase['IsChurned'] = (customer_last_purchase['DaysSinceLastPurchase'] > inactivity_days).astype(int)

        churn_rate = customer_last_purchase['IsChurned'].mean()
        logger.info(f"Churn rate (>{inactivity_days} days inactive): {churn_rate:.2%}")

        return customer_last_purchase, inactivity_days

    def calculate_monthly_retention_rate(self):
        df = self.df.copy()
        df['YearMonth'] = df['InvoiceDate'].dt.to_period('M')

        monthly_customers = df.groupby('YearMonth')['Customer ID'].nunique().reset_index()
        monthly_customers.columns = ['YearMonth', 'ActiveCustomers']

        monthly_customers['YearMonth'] = monthly_customers['YearMonth'].astype(str)

        logger.info(f"\nMonthly Active Customers:\n{monthly_customers}")

        return monthly_customers

if __name__ == "__main__":
    df = pd.read_csv('data/transactions_clean.csv')

    ra = RetentionAnalysis(df)

    logger.info("=" * 60)
    logger.info("RETENTION ANALYSIS")
    logger.info("=" * 60)

    retention_table, cohort_pivot = ra.calculate_cohort_retention()

    churn_df, inactivity_window = ra.calculate_churn_definition()
    churn_df.to_csv('data/customer_churn_status.csv', index=False)
    logger.info(f"Saved churn status to customer_churn_status.csv")

    monthly_retention = ra.calculate_monthly_retention_rate()
    monthly_retention.to_csv('data/monthly_retention.csv', index=False)

    retention_table.to_csv('data/cohort_retention_table.csv')
    cohort_pivot.to_csv('data/cohort_retention_pivot.csv')
    logger.info("Saved cohort retention table to cohort_retention_table.csv and raw counts to cohort_retention_pivot.csv")
