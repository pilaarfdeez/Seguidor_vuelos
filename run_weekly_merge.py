import os
import pandas as pd
from config.logging import init_logger

logger = init_logger(__name__)


def merge_weekly_data():

    RAW_FILE = "data/results/raw/weekly_results.parquet"
    PROCESSED_PATH = "data/results/processed"
    MASTER_FILE = os.path.join(PROCESSED_PATH, "results.parquet")

    weekly_df = pd.read_parquet(RAW_FILE)

    os.makedirs(PROCESSED_PATH, exist_ok=True)

    if os.path.exists(MASTER_FILE):
        master_df = pd.read_parquet(MASTER_FILE)
        combined_df = pd.concat([master_df, weekly_df], ignore_index=True)
    else:
        combined_df = weekly_df

    combined_df.to_parquet(MASTER_FILE, index=False)
    logger.info(f"Successfully merged weekly database into {MASTER_FILE}")
    return True

if __name__ == "__main__":
    if not merge_weekly_data():
        exit(1)
