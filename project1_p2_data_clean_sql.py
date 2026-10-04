# 2. Data Preparation (Data Cleaning)

import pymysql
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st
from pathlib import Path

# 1. Load Data

# 1.1 Load the dataset directly from CSV file and check the data
df_csv = pd.read_csv("global_seismic_trends_project_1.csv")

# print("Rows:", df_csv.shape[0])
# print("Columns:", df_csv.shape[1])
# print(df_csv.head())

df = df_csv.copy()

# 1.2 Convert date/time fields (time, updated) to datetime objects.
# Convert date/time fields to datetime

df["time"] = pd.to_datetime(df["time"], errors="coerce")
df["updated"] = pd.to_datetime(df["updated"], errors="coerce")

#print(df[["time", "updated"]].dtypes)
#print(df[["time", "updated"]].head())

# 2. Clean Text Fields

# 2.1 Use Regex to extract country from place.
df["country"] = df["place"].str.extract(r",\s*(.+)$")

# print(df["country"].head())

# 2.2  Normalize alert field (if exists) to lowercase
if "alert" in df.columns:
    df["alert"] = df["alert"].str.lower()

# print(df["alert"].value_counts())

# 2.3 Ensure all string fields (magType, status, type, net, sources, types) are clean.
text_columns = ["magType", "status", "type", "net", "sources", "types"]

for column in text_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .replace("", pd.NA)
    )

# print(df[text_columns].head())

# 3. Clean Numeric Fields

# 3.1 Convert mag, depth_km, nst, dmin, rms, gap, magError, depthError, magNst, sig to numeric.
numeric_columns = [
    "mag", "depth_km", "nst", "dmin", "rms", "gap",
    "magError", "depthError", "magNst", "sig"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# print(df[[column for column in numeric_columns if column in df.columns]].dtypes)

# 3.2 Fill missing numeric values with 0 or median if needed.
for column in numeric_columns:
    if column in df.columns:
        median_value = df[column].median()
        if pd.notna(median_value):
            df[column] = df[column].fillna(median_value)

# print(df[[column for column in numeric_columns if column in df.columns]].isna().sum())

# 4. Add Derived Columns

# 4.1 Year, month, day, day_of_week from time.
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
df["day"] = df["time"].dt.day
df["day_of_week"] = df["time"].dt.day_name()

# print(df[["time", "year", "month", "day", "day_of_week"]].head())

# 4.2 Shallow/deep earthquake flag based on depth_km.
df["depth_category"] = df["depth_km"].apply(
    lambda depth: "Unknown" if pd.isna(depth)
    else "Shallow" if depth < 70
    else "Deep"
)

# print(df[["depth_km", "depth_category"]].head())

# 4.3 Strong/destructive flag based on mag thresholds.
df["strong_flag"] = df["mag"] >= 6.0
df["potentially_destructive_flag"] = df["mag"] >= 7.0

# print(df[["mag", "strong_flag", "potentially_destructive_flag"]].head())

# Saving the raw data to a CSV file for Backup
csv_path = Path(__file__).with_name("global_seismic_trends_project_2.csv")
df.to_csv(csv_path, index=False)
print(f"Raw data saved to: {csv_path}")

# 5. Store Cleaned Data into MySQL Database
from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:1234@localhost:3306/global_seismic_trends"
)

df.to_sql(
    name="earthquakes",
    con=engine,
    if_exists="replace",
    index=False,
)

print("Cleaned data saved to the earthquakes table.")