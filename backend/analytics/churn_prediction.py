import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
import pickle
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChurnPredictor:
    def __init__(self, features_df: pd.DataFrame, churn_df: pd.DataFrame):
        self.features_df = features_df.copy()
        self.churn_df = churn_df.copy()

        self.model = None
        self.scaler = None
        self.feature_cols = None

    def prepare_data(self):
        df = self.features_df.merge(
            self.churn_df[['Customer ID', 'IsChurned']],
            on='Customer ID',
            how='left'
        )

        feature_cols = [
            'Recency', 'Frequency', 'Monetary_Total', 'Monetary_Avg',
            'Monetary_Std', 'Transaction_Count', 'CustomerLifespan_Days',
            'UniqueProdCategories', 'MaxTransactionAmount', 'AvgDaysBetweenPurchases',
            'R_Score', 'F_Score', 'M_Score'
        ]

        df = df.dropna(subset=feature_cols + ['IsChurned'])

        X = df[feature_cols].copy()
        y = df['IsChurned'].copy()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        self.feature_cols = feature_cols
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.df = df

        logger.info(f"Training set: {X_train.shape[0]} samples, {X_test.shape[0]} test samples")
        logger.info(f"Churn distribution in train: {y_train.value_counts().to_dict()}")
        logger.info(f"Churn distribution in test: {y_test.value_counts().to_dict()}")

        return X_train, X_test, y_train, y_test

    def train_logistic_regression(self):
        logger.info("Training Logistic Regression...")
        model = LogisticRegression(max_iter=1000, random_state=42)
        model.fit(self.X_train, self.y_train)

        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]

        accuracy = (y_pred == self.y_test).mean()
        auc = roc_auc_score(self.y_test, y_pred_proba)

        logger.info(f"Logistic Regression - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")

        return model, accuracy, auc

    def train_random_forest(self):
        logger.info("Training Random Forest...")
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(self.X_train, self.y_train)

        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]

        accuracy = (y_pred == self.y_test).mean()
        auc = roc_auc_score(self.y_test, y_pred_proba)

        logger.info(f"Random Forest - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")

        feature_importance = pd.DataFrame({
            'Feature': self.feature_cols,
            'Importance': model.feature_importances_
        }).sort_values('Importance', ascending=False)

        logger.info(f"\nTop 10 Features:\n{feature_importance.head(10)}")

        return model, accuracy, auc, feature_importance

    def train_xgboost(self):
        logger.info("Training XGBoost...")
        model = xgb.XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42,
            verbosity=0
        )
        model.fit(self.X_train, self.y_train)

        y_pred = model.predict(self.X_test)
        y_pred_proba = model.predict_proba(self.X_test)[:, 1]

        accuracy = (y_pred == self.y_test).mean()
        auc = roc_auc_score(self.y_test, y_pred_proba)

        logger.info(f"XGBoost - Accuracy: {accuracy:.4f}, AUC: {auc:.4f}")

        return model, accuracy, auc

    def select_best_model(self):
        lr_model, lr_acc, lr_auc = self.train_logistic_regression()
        rf_model, rf_acc, rf_auc, rf_importance = self.train_random_forest()
        xgb_model, xgb_acc, xgb_auc = self.train_xgboost()

        models = {
            'LogisticRegression': (lr_model, lr_auc),
            'RandomForest': (rf_model, rf_auc),
            'XGBoost': (xgb_model, xgb_auc)
        }

        best_model_name = max(models, key=lambda x: models[x][1])
        best_model = models[best_model_name][0]

        logger.info(f"\nBest model: {best_model_name} (AUC: {models[best_model_name][1]:.4f})")

        self.model = best_model
        return best_model, best_model_name

    def generate_churn_scores(self):
        if self.model is None:
            self.select_best_model()

        churn_scores = self.df.copy()
        churn_scores['ChurnScore'] = self.model.predict_proba(
            self.df[self.feature_cols]
        )[:, 1]

        churn_scores = churn_scores.sort_values('ChurnScore', ascending=False)

        logger.info(f"\nTop 10 At-Risk Customers:")
        logger.info(churn_scores[['Customer ID', 'ChurnScore', 'Recency', 'Frequency', 'Monetary_Total']].head(10))

        return churn_scores[['Customer ID', 'ChurnScore', 'IsChurned']]

if __name__ == "__main__":
    features = pd.read_csv('data/customer_features.csv')
    churn = pd.read_csv('data/customer_churn_status.csv')

    cp = ChurnPredictor(features, churn)
    cp.prepare_data()

    best_model, best_name = cp.select_best_model()

    churn_scores = cp.generate_churn_scores()
    churn_scores.to_csv('data/customer_churn_scores.csv', index=False)

    logger.info(f"Saved churn scores to customer_churn_scores.csv")

    with open('data/churn_model.pkl', 'wb') as f:
        pickle.dump(cp.model, f)
    logger.info(f"Saved model to churn_model.pkl")
