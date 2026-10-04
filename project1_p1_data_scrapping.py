# Global Seismic Trends: Data-Driven Earthquake Insights

# 1 Data Scrapping 

import requests
from datetime import datetime, timedelta
import pandas as pd
import pymysql
from sqlalchemy import create_engine
from pathlib import Path

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

all_records = []

today = datetime.now()                                    # Current date and year
current_year = today.year
current_month = today.month

start_year = current_year - 4                              # Last 5 years

for year in range(start_year, current_year + 1):

    if year == current_year:                               # For current year, stop at current month
        last_month = current_month
    else:
        last_month = 12

    for month in range(1, last_month + 1):

        start_date = f"{year}-{month:02d}-01"

        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        if year == current_year and month == current_month:  # For the current month, use today's date as end date
            end_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")

        params = {
            "starttime": start_date,
            "endtime": end_date,
            "format": "geojson",
            "minmagnitude": 3
        }

        response = requests.get(url, params=params)   # Checking API request
        if response.status_code != 200:
            print(f"Error fetching data for {start_date} to {end_date}: {response.status_code}")
            continue
        try:
            data = response.json()
        except Exception as e:
            print(f"Error parsing JSON for {start_date} : {e}")
            continue

        for f in data['features']:                     # Extract data using for loop in features list 
             p = f['properties']                                                    
             g = f['geometry']['coordinates']
             all_records.append({  
                    "id": f.get("id"),                                                # 1.Id
                    "time": pd.to_datetime(p.get("time"),unit='ms'),                  # 2.Time
                    "updated": pd.to_datetime(p.get("updated"),unit="ms"),            # 3.Updated Time 
                    "latitude": g[1] if g else None,                                  # 4.Latitude of Earthquake
                    "longitude": g[0] if g else None,                                 # 5.Longitude of Earthquake
                    "depth_km": g[2] if g else None,                                  # 6.Depth of Earthquake in Kilometers
                    "mag": p.get("mag"),                                              # 7.Magnitude of Earthquake
                    "magType": p.get("magType"),                                      # 8.Type of Magnitude
                    "place": p.get("place"),                                          # 9.Place(Location)
                    "status": p.get("status"),                                        # 10.Status 
                    "tsunami": p.get("tsunami"),                                      # 11.Tsunami
                    "sig": p.get("sig"),                                              # 12.Siginificance Score
                    "net": p.get("net"),                                              # 13.Network Id
                    "nst": p.get("nst"),                                              # 14.Number of seismic stations
                    "dmin": p.get("dmin"),                                            # 15.Minimum distance to stations
                    "rms": p.get("rms"),                                              # 16.Root mean square of residuals
                    "gap": p.get("gap"),                                              # 17.Azimuthal gap
                    "code": p.get("code"),                                            # 18.Code 
                    "alert": p.get("alert"),                                          # 19.Alert
                    "cdi":p.get("cdi"),                                               # 20.Community Internet Intensity 
                    "mmi":p.get("mmi"),                                               # 21.Modified Mercalli Intensity
                    "felt":p.get("felt"),                                             # 22.Felt
                    "types": p.get("types"),                                          # 23.Types of associated data
                    "ids": p.get("ids"),                                              # 24.Comma-sperated list
                    "sources": p.get("sources"),                                      # 25.Reporting sources 
                    "type": p.get("type")                                             # 26.Type of seismic event                          
                })

df = pd.DataFrame(all_records)

print("Rows and columns:", df.shape)
print(df.head())
df.info()

# Connecting to MySQL database and storing the data into a table

try:
    # Connect to MySQL without selecting a database
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="1234",
        port=3306
    )

    # Create the database if it does not exist yet
    with connection.cursor() as cursor:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS global_seismic_trends"
        )

    connection.close()

    # Connect to the database and save the DataFrame
    engine = create_engine(
        "mysql+pymysql://root:1234@localhost:3306/global_seismic_trends"
    )

    df.to_sql(
        name="earthquake_table",
        con=engine,
        if_exists="append",
        index=False
    )

    print("Data inserted into MySQL successfully!")

except Exception as e:
    print(f"Error connecting to MySQL: {e}")

# Saving the raw data to a CSV file for Data Cleaning Process
csv_path = Path(__file__).with_name("global_seismic_trends_project_1.csv")
df.to_csv(csv_path, index=False)
print(f"Raw data saved to: {csv_path}")