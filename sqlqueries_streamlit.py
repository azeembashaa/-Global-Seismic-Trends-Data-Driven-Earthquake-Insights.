# 4. SQL Analyst Task

from ast import For

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# Connecting to MySQL database using SQLAlchemy
engine = create_engine('mysql+pymysql://root:1234@localhost:3306/global_seismic_trends')

# Title
st.title("Global Seismic Trends: Data-Driven Earthquakes Insights")

# Header
st.header("Earthquake Data Overview")

# Fetching data from MySQL database 
df = pd.read_sql("SELECT * FROM earthquakes", con=engine)

st.dataframe(df)

st.markdown(f"Total Rows: **{len(df):,}**")
st.markdown(f"Total Columns: **{len(df.columns):,}**")

# 26 SQL Queries 

# Magnitude and Depth
st.header("Magnitude and Depth")

# 1. Top 10 strongest earthquakes (mag).

st.subheader("1. Top 10 Strongest Earthquakes")

df1 = pd.read_sql("SELECT * FROM earthquakes ORDER BY mag DESC LIMIT 10", con=engine)
st.dataframe(df1)

# 2. Top 10 deepest earthquakes (depth_km).

st.subheader("2. Top 10 Deepest Earthquakes")

df2 = pd.read_sql("SELECT * FROM earthquakes ORDER BY depth_km DESC LIMIT 10", con=engine)
st.dataframe(df2)

# 3. Shallow earthquakes < 50 km and mag > 7.5.

st.subheader("3. Shallow Earthquakes < 50 km with Magnitude > 7.5")

df3 = pd.read_sql("SELECT * FROM earthquakes WHERE depth_km < 50 AND mag > 7.5", con=engine)
st.dataframe(df3)

# 5. Average magnitude per magnitude type (magType).

st.subheader("5. Average Magnitude per Magnitude Type")

df5 = pd.read_sql("SELECT magType, AVG(mag) as avg_mag FROM earthquakes GROUP BY magType", con=engine)
st.dataframe(df5)

# Time Analysis
st.header("Time Analysis")

# 6. Year with most earthquakes

st.subheader("6. Year with Most Earthquakes")

df6 = pd.read_sql(
    """
    SELECT year, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY year
    ORDER BY earthquake_count DESC
    LIMIT 1
    """,
    con=engine
)

st.dataframe(df6)

# 7. Month with highest number of earthquakes.

st.subheader("7. Month with Highest Number of Earthquakes")

df7 = pd.read_sql(
    """
    SELECT month, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY month
    ORDER BY earthquake_count DESC
    LIMIT 1
    """,
    con=engine
)

st.dataframe(df7)

# 8. Day of week with most earthquakes.

st.subheader("8. Day of Week with Most Earthquakes")

df8 = pd.read_sql(
    """
    SELECT day_of_week, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY day_of_week
    ORDER BY earthquake_count DESC
    LIMIT 1
    """,
    con=engine
)

st.dataframe(df8)

# 9. Count of earthquakes per hour of day
st.subheader("9. Earthquake Count per Hour of Day")

df9 = pd.read_sql(
    """
   SELECT HOUR(`time`) AS hour, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY HOUR(`time`)
    ORDER BY hour
    """,
    con=engine
)

st.dataframe(df9)

# 10. Most active reporting network (net).

st.subheader("10. Most Active Reporting Network")

df10 = pd.read_sql(
    """
    SELECT net, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE net IS NOT NULL AND net != ''
    GROUP BY net
    ORDER BY earthquake_count DESC
    LIMIT 1
    """,
    con=engine
)

st.dataframe(df10)

# Casualties & Economic Loss
st.header("Casualties & Economic Loss")

# 11. Top 5 places with highest casualties.

st.subheader("11. Top 5 Places with Highest Casualties")

df11 = pd.read_sql(
    """
    SELECT place, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE place IS NOT NULL AND place != ''
    GROUP BY place
    ORDER BY earthquake_count DESC
    LIMIT 5
    """,
    con=engine
)

st.dataframe(df11)

# 13. Average economic loss by alert level.
st.subheader("13. Average Economic Loss by Alert Level")

df13 = pd.read_sql(
    """
    SELECT alert, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE alert IS NOT NULL AND alert != ''
    GROUP BY alert
    ORDER BY earthquake_count DESC
    """,
    con=engine
)

st.dataframe(df13)

# Event Type & Quality Metrics
st.header("Event Type & Quality Metrics")

# 14. Count of reviewed vs automatic earthquakes (status).

st.subheader("14. Count of Reviewed vs Automatic Earthquakes")

df14 = pd.read_sql(
    """
    SELECT status, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE status IS NOT NULL AND status != ''
    GROUP BY status
    ORDER BY earthquake_count DESC
    """,
    con=engine
)

st.dataframe(df14)

# 15. Count by earthquake type (type).

st.subheader("15. Count by Earthquake Type")

df15 = pd.read_sql(
    """
    SELECT type, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE type IS NOT NULL AND type != ''
    GROUP BY type
    ORDER BY earthquake_count DESC
    """,
    con=engine
)

st.dataframe(df15)

# 16. Number of earthquakes by data type (types).

st.subheader("16. Number of Earthquakes by Data Type")

df16 = pd.read_sql(
    """
    SELECT types, COUNT(*) AS earthquake_count
    FROM earthquakes
    GROUP BY types
    ORDER BY earthquake_count DESC
    """,
    con=engine
)

st.dataframe(df16)

# 18. Events with high station coverage (nst > threshold).

st.subheader("18. Events with High Station Coverage")

df18 = pd.read_sql(
    """
    SELECT id, time, place, mag, nst
    FROM earthquakes
    WHERE nst > 50
    ORDER BY nst DESC
    """,
    con=engine
)

st.dataframe(df18)

# Tsunamis & Alerts
st.header("Tsunamis & Alerts")

# 19. Number of tsunamis triggered per year.

st.subheader("19. Number of Tsunamis Triggered per Year")

df19 = pd.read_sql(
    """
    SELECT year,
           SUM(CASE WHEN tsunami = 1 THEN 1 ELSE 0 END) AS tsunami_count
    FROM earthquakes
    GROUP BY year
    ORDER BY year
    """,
    con=engine
)

st.dataframe(df19)

# 20. Count earthquakes by alert levels (red, orange, etc.).

st.subheader("20. Count of Earthquakes by Alert Levels")

df20 = pd.read_sql(
    """
    SELECT alert, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE alert IS NOT NULL AND TRIM(alert) <> ''
    GROUP BY alert
    ORDER BY earthquake_count DESC
    """,
    con=engine
)

st.dataframe(df20)

# Seismic Pattern & Trends Analysis.
st.header("Seismic Pattern & Trends Analysis")

# 21. Find the top 5 countries with the highest average magnitude of earthquakes in the past 5 years

st.subheader("21. Top 5 Countries by Average Earthquake Magnitude")

df21 = pd.read_sql(
    """
    SELECT country, AVG(mag) AS average_magnitude, COUNT(*) AS earthquake_count
    FROM earthquakes
    WHERE `time` >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
      AND country IS NOT NULL
      AND TRIM(country) <> ''
      AND mag IS NOT NULL
    GROUP BY country
    ORDER BY average_magnitude DESC
    LIMIT 5
    """,
    con=engine
)

st.dataframe(df21)

# 22. Find countries that have experienced both shallow and deep earthquakes within the same month.

st.subheader("22. Countries with Both Shallow and Deep Earthquakes in the Same Month")

df22 = pd.read_sql(
    """
    SELECT country, year, month,
           SUM(CASE WHEN depth_category = 'Shallow' THEN 1 ELSE 0 END)
               AS shallow_count,
           SUM(CASE WHEN depth_category = 'Deep' THEN 1 ELSE 0 END)
               AS deep_count
    FROM earthquakes
    WHERE country IS NOT NULL AND TRIM(country) <> ''
    GROUP BY country, year, month
    HAVING shallow_count > 0 AND deep_count > 0
    ORDER BY year, month, country
    """,
    con=engine
)

st.dataframe(df22)

# 23. Compute the year-over-year growth rate in the total number of earthquakes globally.

st.subheader("23. Year-over-Year Growth Rate in Total Earthquakes Globally")

df23 = pd.read_sql("""
    SELECT year, COUNT(*) AS earthquake_count,
           ROUND(
               (COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY year))
               * 100.0 / NULLIF(LAG(COUNT(*)) OVER (ORDER BY year), 0),
               2
           ) AS growth_rate
    FROM earthquakes
    GROUP BY year
    ORDER BY year
""", con=engine)

st.dataframe(df23)

# 24. List the 3 most seismically active regions by combining both frequency and average magnitude.

st.subheader("24. Most Seismically Active Regions by Frequency and Average Magnitude")

df24 = pd.read_sql("""
    SELECT country AS region,
           COUNT(*) AS earthquake_count,
           ROUND(AVG(mag), 2) AS average_magnitude
    FROM earthquakes
    WHERE country IS NOT NULL AND country <> ''
    GROUP BY country
    ORDER BY earthquake_count DESC, average_magnitude DESC
    LIMIT 3
""", con=engine)

st.dataframe(df24)

# Depth, Location & Distance-Based  Analysis.
st.header("Depth, Location & Distance-Based Analysis")

#25. For each country, calculate the average depth of earthquakes within ±5° latitude range of the equator.

st.subheader("25. Average Depth of Earthquakes within ±5° Latitude Range of the Equator by Country")

df25 = pd.read_sql("""
    SELECT country, ROUND(AVG(depth_km), 2) AS average_depth_km
    FROM earthquakes
    WHERE latitude BETWEEN -5 AND 5
      AND country IS NOT NULL AND country <> ''
    GROUP BY country
    ORDER BY average_depth_km DESC
""", con=engine)

st.dataframe(df25)

#  26. Identify countries having the highest ratio of shallow to deep earthquakes.

st.subheader("26. Countries with Highest Ratio of Shallow to Deep Earthquakes")

df26 = pd.read_sql("""
    SELECT country,
           SUM(depth_category = 'Shallow') AS shallow_count,
           SUM(depth_category = 'Deep') AS deep_count,
           ROUND(
               SUM(depth_category = 'Shallow') /
               NULLIF(SUM(depth_category = 'Deep'), 0),
               2
           ) AS shallow_deep_ratio
    FROM earthquakes
    WHERE country IS NOT NULL AND country <> ''
    GROUP BY country
    HAVING deep_count > 0
    ORDER BY shallow_deep_ratio DESC
    LIMIT 5
""", con=engine)

st.dataframe(df26)

#  27. Find the average magnitude difference between earthquakes with tsunami alerts and those without.

st.subheader("27. Average Magnitude Difference Between Earthquakes with Tsunami Alerts and Those Without")

df27 = pd.read_sql("""
    SELECT
        ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END), 2) AS tsunami_avg_mag,
        ROUND(AVG(CASE WHEN tsunami = 0 THEN mag END), 2) AS no_tsunami_avg_mag,
        ROUND(
            AVG(CASE WHEN tsunami = 1 THEN mag END) -
            AVG(CASE WHEN tsunami = 0 THEN mag END),
            2
        ) AS average_magnitude_difference
    FROM earthquakes
""", con=engine)

st.dataframe(df27)

# 28. Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins).

st.subheader("28. Events with Lowest Data Reliability (Highest Average Error Margins)")

df28 = pd.read_sql("""
    SELECT id, time, place, mag, gap, rms
    FROM earthquakes
    WHERE gap > (SELECT AVG(gap) FROM earthquakes)
      AND rms > (SELECT AVG(rms) FROM earthquakes)
    ORDER BY gap DESC, rms DESC
    LIMIT 10
""", con=engine)

st.dataframe(df28)

# 30. Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km).

st.subheader("30. Regions with Highest Frequency of Deep-Focus Earthquakes (Depth > 300 km)")

df30 = pd.read_sql("""
    SELECT country AS region, COUNT(*) AS deep_earthquake_count
    FROM earthquakes
    WHERE depth_km > 300
      AND country IS NOT NULL AND country <> ''
    GROUP BY country
    ORDER BY deep_earthquake_count DESC
    LIMIT 10
""", con=engine)

st.dataframe(df30)
