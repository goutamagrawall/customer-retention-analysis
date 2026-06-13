import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BehavioralSegmentation:
    def __init__(self, features_df: pd.DataFrame):
        self.features_df = features_df.copy()
        self.scaler = StandardScaler()
        self.kmeans = None

    def prepare_features_for_clustering(self):
        feature_cols = [
            'Recency', 'Frequency', 'Monetary_Total', 'Monetary_Avg',
            'Monetary_Std', 'Transaction_Count', 'CustomerLifespan_Days',
            'UniqueProdCategories', 'MaxTransactionAmount', 'AvgDaysBetweenPurchases'
        ]

        X = self.features_df[feature_cols].copy()
        X = X.fillna(0)

        X_scaled = self.scaler.fit_transform(X)

        logger.info(f"Features prepared for clustering: {X_scaled.shape}")

        return X_scaled, feature_cols

    def find_optimal_clusters(self, X_scaled: np.ndarray, max_k: int = 8):
        inertias = []
        silhouette_scores = []
        K_range = range(2, max_k + 1)

        for k in K_range:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
            sil_score = silhouette_score(X_scaled, kmeans.labels_)
            silhouette_scores.append(sil_score)
            logger.info(f"K={k}: Silhouette Score = {sil_score:.4f}")

        optimal_k = K_range[np.argmax(silhouette_scores)]
        logger.info(f"\nOptimal number of clusters: {optimal_k} (Silhouette: {max(silhouette_scores):.4f})")

        return optimal_k

    def train_clustering(self, X_scaled: np.ndarray, n_clusters: int = 5):
        logger.info(f"Training K-Means with k={n_clusters}...")

        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.kmeans.fit(X_scaled)

        labels = self.kmeans.labels_

        logger.info(f"Cluster distribution:\n{pd.Series(labels).value_counts().sort_index()}")

        return labels

    def profile_clusters(self, labels: np.ndarray, feature_cols: list):
        df = self.features_df.copy()
        df['Cluster'] = labels

        profiles = []
        for cluster_id in sorted(df['Cluster'].unique()):
            cluster_data = df[df['Cluster'] == cluster_id]
            profile = {
                'Cluster': cluster_id,
                'Size': len(cluster_data),
                'AvgRecency': cluster_data['Recency'].mean(),
                'AvgFrequency': cluster_data['Frequency'].mean(),
                'AvgMonetary': cluster_data['Monetary_Total'].mean(),
                'AvgLifespan': cluster_data['CustomerLifespan_Days'].mean(),
            }
            profiles.append(profile)

        profiles_df = pd.DataFrame(profiles)

        logger.info(f"\nCluster Profiles:\n{profiles_df}")

        cluster_names = {
            0: 'Standard',
            1: 'Emerging',
            2: 'VIP',
            3: 'Inactive',
            4: 'Frequent'
        }

        df['Cluster_Name'] = df['Cluster'].map(cluster_names)

        return df

    def generate_clustering_segments(self):
        X_scaled, feature_cols = self.prepare_features_for_clustering()

        optimal_k = self.find_optimal_clusters(X_scaled, max_k=8)

        optimal_k = 5
        logger.info(f"Using K=5 for business-meaningful segments (overriding silhouette-based optimal)")

        labels = self.train_clustering(X_scaled, n_clusters=optimal_k)

        df_with_clusters = self.profile_clusters(labels, feature_cols)

        return df_with_clusters

if __name__ == "__main__":
    features = pd.read_csv('data/customer_features.csv')

    bs = BehavioralSegmentation(features)
    df_clustered = bs.generate_clustering_segments()

    df_clustered[['Customer ID', 'Cluster', 'Cluster_Name']].to_csv(
        'data/customer_clustering_segments.csv',
        index=False
    )

    logger.info("Saved clustering segments to customer_clustering_segments.csv")
