import pandas as pd
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, df: pd.DataFrame, reference_date: pd.Timestamp = None):
        self.df = df.copy()
        self.reference_date = reference_date or df['InvoiceDate'].max()
        logger.info(f"Reference date: {self.reference_date}")

    def calculate_rfm(self) -> pd.DataFrame:
        df = self.df.copy()
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

        rfm = df.groupby('Customer ID').agg({
            'InvoiceDate': lambda x: (self.reference_date - x.max()).days,
            'Invoice': 'nunique',
            'TransactionAmount': ['sum', 'mean', 'std', 'count']
        }).reset_index()

        rfm.columns = ['Customer ID', 'Recency', 'Frequency', 'Monetary_Total',
                       'Monetary_Avg', 'Monetary_Std', 'Transaction_Count']

        rfm['Monetary_Std'] = rfm['Monetary_Std'].fillna(0)

        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5,
                                  labels=[1, 2, 3, 4, 5], duplicates='drop')
        rfm['M_Score'] = pd.qcut(rfm['Monetary_Total'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')

        rfm['R_Score'] = rfm['R_Score'].astype(int)
        rfm['F_Score'] = rfm['F_Score'].astype(int)
        rfm['M_Score'] = rfm['M_Score'].astype(int)

        rfm['RFM_Segment'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

        return rfm

    def calculate_behavioral_metrics(self) -> pd.DataFrame:
        df = self.df.copy()
        df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

        behavioral = df.groupby('Customer ID').agg({
            'InvoiceDate': ['min', 'max', lambda x: (x.max() - x.min()).days],
            'StockCode': 'nunique',
            'Country': lambda x: x.mode()[0] if len(x.mode()) > 0 else x.iloc[0],
            'TransactionAmount': lambda x: x.nlargest(1).values[0] if len(x) > 0 else 0,
        }).reset_index()

        behavioral.columns = ['Customer ID', 'FirstPurchaseDate', 'LastPurchaseDate',
                              'CustomerLifespan_Days', 'UniqueProdCategories',
                              'Country', 'MaxTransactionAmount']

        behavioral['AvgDaysBetweenPurchases'] = (
            behavioral['CustomerLifespan_Days'] /
            df.groupby('Customer ID')['Invoice'].nunique().reset_index()['Invoice']
        ).values

        return behavioral

    def create_rule_based_segments(self, rfm: pd.DataFrame) -> pd.DataFrame:
        rfm_copy = rfm.copy()

        rfm_copy['Rule_Segment'] = 'Standard'

        # 1. Loyal (R >= 4, F >= 3)
        rfm_copy.loc[
            (rfm_copy['R_Score'] >= 4) & (rfm_copy['Frequency'] >= 3),
            'Rule_Segment'
        ] = 'Loyal'

        # 2. HighEngagement_LowValue (R >= 3, F >= 3, M <= 25th percentile)
        rfm_copy.loc[
            (rfm_copy['R_Score'] >= 3) & (rfm_copy['Frequency'] >= 3) & (rfm_copy['Monetary_Total'] <= rfm_copy['Monetary_Total'].quantile(0.25)),
            'Rule_Segment'
        ] = 'HighEngagement_LowValue'

        # 3. Dormant (R <= 2, F <= 2)
        rfm_copy.loc[
            (rfm_copy['R_Score'] <= 2) & (rfm_copy['Frequency'] <= 2),
            'Rule_Segment'
        ] = 'Dormant'

        # 4. At_Risk_HighValue (R <= 2, M > 75th percentile)
        rfm_copy.loc[
            (rfm_copy['R_Score'] <= 2) & (rfm_copy['Monetary_Total'] > rfm_copy['Monetary_Total'].quantile(0.75)),
            'Rule_Segment'
        ] = 'At_Risk_HighValue'

        # 5. Champions (R >= 4, F >= 4, M >= 4) - Highest priority, overrides Loyal
        rfm_copy.loc[
            (rfm_copy['R_Score'] >= 4) & (rfm_copy['F_Score'] >= 4) & (rfm_copy['M_Score'] >= 4),
            'Rule_Segment'
        ] = 'Champions'

        return rfm_copy

    def generate_all_features(self):
        logger.info("Calculating RFM scores...")
        rfm = self.calculate_rfm()
        logger.info(f"RFM shape: {rfm.shape}")

        logger.info("Calculating behavioral metrics...")
        behavioral = self.calculate_behavioral_metrics()
        logger.info(f"Behavioral shape: {behavioral.shape}")

        logger.info("Creating rule-based segments...")
        rfm = self.create_rule_based_segments(rfm)

        features = rfm.merge(behavioral, on='Customer ID', how='left')

        return features

if __name__ == "__main__":
    df = pd.read_csv('data/transactions_clean.csv')
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

    fe = FeatureEngineer(df)
    features = fe.generate_all_features()

    features.to_csv('data/customer_features.csv', index=False)
    logger.info(f"Saved {len(features)} customer features to customer_features.csv")
    logger.info("\nFeature Summary:")
    logger.info(features[['Recency', 'Frequency', 'Monetary_Total', 'RFM_Segment', 'Rule_Segment']].describe())
