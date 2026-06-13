import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_raw_data(filepath: str) -> pd.DataFrame:
    excel_file = pd.ExcelFile(filepath)
    dfs = [pd.read_excel(filepath, sheet_name=sheet) for sheet in excel_file.sheet_names]
    df = pd.concat(dfs, ignore_index=True)
    logger.info(f"Loaded {len(df)} rows from {len(excel_file.sheet_names)} sheets")
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df_clean = df.copy()

    logger.info(f"Original shape: {df_clean.shape}")

    df_clean = df_clean.dropna(subset=['Customer ID'])
    logger.info(f"After removing null Customer IDs: {df_clean.shape}")

    df_clean = df_clean[df_clean['Quantity'] > 0]
    logger.info(f"After filtering Quantity > 0: {df_clean.shape}")

    df_clean = df_clean[df_clean['Price'] > 0]
    logger.info(f"After filtering Price > 0: {df_clean.shape}")

    df_clean['Customer ID'] = df_clean['Customer ID'].astype(int)
    df_clean['Quantity'] = df_clean['Quantity'].astype(int)

    df_clean['TransactionAmount'] = df_clean['Quantity'] * df_clean['Price']

    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])

    return df_clean

def save_processed_data(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    input_file = Path(__file__).parent.parent.parent / "data" / "online_retail_II.xlsx"
    output_file = Path(__file__).parent.parent.parent / "data" / "transactions_clean.csv"

    df = load_raw_data(str(input_file))
    df_clean = clean_data(df)
    save_processed_data(df_clean, str(output_file))

    logger.info(f"\nData Summary:")
    logger.info(f"Date range: {df_clean['InvoiceDate'].min()} to {df_clean['InvoiceDate'].max()}")
    logger.info(f"Unique customers: {df_clean['Customer ID'].nunique()}")
    logger.info(f"Unique products: {df_clean['StockCode'].nunique()}")
    logger.info(f"Total revenue: ${df_clean['TransactionAmount'].sum():,.2f}")
