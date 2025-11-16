import numpy as np
import os
import pandas as pd
import re
import datetime as dt

from config.logging import init_logger

logger = init_logger(__name__)

def save_results(flights_df: pd.DataFrame):
  # Remove unnecessary columns
  col_list = flights_df.columns.to_list()
  cols_to_delete = ['Layover', 'CO2 Emission (kg)', 'Emission Diff (%)', 'Arrival datetime']
  col_list = [col for col in col_list if col not in cols_to_delete]
  df = flights_df[col_list].copy()  # <-- .copy() to avoid SettingWithCopyWarning
  df.dropna(inplace=True)

  # Parse travel time to minutes
  for i in range(len(df)):
      hours = 0
      minutes = 0
      match = re.search(r"(?:(\d+)\s*hr)?\s*(?:(\d+)\s*min)?", df['Travel Time'].iloc[i])
      if match:
          if match.group(1):
              hours = int(match.group(1))
          if match.group(2):
              minutes = int(match.group(2))
      df.at[df.index[i], 'travel_time_minutes'] = dt.timedelta(hours=hours, minutes=minutes).seconds // 60
  df['travel_time_minutes'] = df['travel_time_minutes'].astype(int)

  # Calculate days left until departure
  df['days_left'] = (pd.to_datetime(df.loc[:, 'Departure datetime']) - pd.to_datetime(df.loc[:, 'Search Date'])).dt.days
  df.drop(columns=['Search Date', 'Travel Time'], inplace=True)

  # Rename columns to snake_case
  rename_dict = {
      'Origin': 'origin',
      'Destination': 'destination',
      'Departure datetime': 'departure_datetime',
      'Airline(s)': 'airline',
      'Num Stops': 'num_stops',
      'Price': 'price_eur',
  }
  df.rename(columns=rename_dict, inplace=True)

  # Ensure output directories exist
  parquet_dir = 'data/results/raw'
  preview_csv_path = os.path.join(parquet_dir, 'preview.csv')
  parquet_path = os.path.join(parquet_dir, 'weekly_results.parquet')
  os.makedirs(parquet_dir, exist_ok=True)

  # Save result df to database
  try:
      existing_df = pd.read_parquet(parquet_path)
      # Filter out rows where all columns except 'price_eur' are already present in existing_df
      compare_cols = [col for col in df.columns if col != 'price_eur']
      if not existing_df.empty:
          # Only keep rows in df that are not duplicated in existing_df (excluding price_eur)
          merged = df.merge(existing_df[compare_cols], on=compare_cols, how='left', indicator=True)
          df = df[merged['_merge'] == 'left_only'].copy()
  except FileNotFoundError:
      existing_df = pd.DataFrame()

  updated_df = pd.concat([existing_df, df], ignore_index=True)
  updated_df.to_parquet(parquet_path, index=False)
  logger.debug(f"Saved {len(df)} new results to database (total: {len(updated_df)})")
  logger.debug(f"Database size: {updated_df.memory_usage(deep=True).sum() / 1024**2:.4f} MB")
  logger.debug(f"New results:\n{df.head(5)}")

  # Save one random row from the new results to a CSV sample file
  if not df.empty:
      sample_row = df.sample(n=1, random_state=42)
      if os.path.exists(preview_csv_path):
          sample_df = pd.read_csv(preview_csv_path)
      else:
          sample_df = pd.DataFrame()

      sample_df = pd.concat([sample_df, sample_row], ignore_index=True)
      sample_df.to_csv(preview_csv_path, index=False)
