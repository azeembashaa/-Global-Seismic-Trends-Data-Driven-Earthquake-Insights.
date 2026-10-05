import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


st.set_page_config(page_title="Global Seismic Trends", layout="wide")
st.title("Global Seismic Trends: Data-Driven Earthquake Insights")

# Connect to the existing MySQL database.
engine = create_engine(
    "mysql+pymysql://root:1234@localhost:3306/global_seismic_trends"
)


@st.cache_data(ttl=300, show_spinner="Loading earthquake table...")
def load_earthquakes():
    return pd.read_sql("SELECT * FROM earthquakes", con=engine)

try:
    df = load_earthquakes()
except Exception as error:
    st.error(f"Could not load the earthquakes table from MySQL: {error}")
    st.stop()

# Keep the overview visible above the query selector.
st.header("Earthquake Data Overview")
st.dataframe(df, height=400, use_container_width=True)
st.markdown(f"**Total rows:** {len(df):,}  \n**Total columns:** {len(df.columns):,}")


# Each dropdown choice runs only its own SQL query.
queries = {
    "1. Top 10 strongest earthquakes": """
        SELECT * FROM earthquakes ORDER BY mag DESC LIMIT 10
    """,
    "2. Top 10 deepest earthquakes": """
        SELECT * FROM earthquakes ORDER BY depth_km DESC LIMIT 10
    """,
    "3. Shallow earthquakes under 50 km with magnitude above 7.5": """
        SELECT * FROM earthquakes
        WHERE depth_km < 50 AND mag > 7.5
        ORDER BY mag DESC
    """,
    "5. Average magnitude by magnitude type": """
        SELECT magType, AVG(mag) AS average_magnitude
        FROM earthquakes GROUP BY magType ORDER BY average_magnitude DESC
    """,
    "6. Year with the most earthquakes": """
        SELECT year, COUNT(*) AS earthquake_count
        FROM earthquakes GROUP BY year
        ORDER BY earthquake_count DESC LIMIT 1
    """,
    "7. Month with the most earthquakes": """
        SELECT month, COUNT(*) AS earthquake_count
        FROM earthquakes GROUP BY month
        ORDER BY earthquake_count DESC LIMIT 1
    """,
    "8. Day of week with the most earthquakes": """
        SELECT day_of_week, COUNT(*) AS earthquake_count
        FROM earthquakes GROUP BY day_of_week
        ORDER BY earthquake_count DESC LIMIT 1
    """,
    "9. Earthquake count by hour of day": """
        SELECT HOUR(`time`) AS hour, COUNT(*) AS earthquake_count
        FROM earthquakes GROUP BY HOUR(`time`) ORDER BY hour
    """,
    "10. Most active reporting network": """
        SELECT net, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE net IS NOT NULL AND net <> ''
        GROUP BY net ORDER BY earthquake_count DESC LIMIT 1
    """,
     "11. Top 5 places by earthquake count": """
        SELECT place, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE place IS NOT NULL AND place <> ''
        GROUP BY place ORDER BY earthquake_count DESC LIMIT 5
    """,
    "13. Earthquake count by alert level": """
        SELECT alert, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE alert IS NOT NULL AND TRIM(alert) <> ''
        GROUP BY alert ORDER BY earthquake_count DESC
    """,
    "14. Reviewed vs automatic earthquakes": """
        SELECT status, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE status IS NOT NULL AND status <> ''
        GROUP BY status ORDER BY earthquake_count DESC
    """,
    "15. Earthquake count by event type": """
        SELECT type, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE type IS NOT NULL AND type <> ''
        GROUP BY type ORDER BY earthquake_count DESC
    """,
    "16. Earthquake count by types combination": """
        SELECT types, COUNT(*) AS earthquake_count
        FROM earthquakes GROUP BY types ORDER BY earthquake_count DESC
    """,
    "18. Events with high station coverage (nst > 50)": """
        SELECT id, `time`, place, mag, nst
        FROM earthquakes WHERE nst > 50 ORDER BY nst DESC
    """,
     "19. Tsunamis triggered per year": """
        SELECT year,
               SUM(CASE WHEN tsunami = 1 THEN 1 ELSE 0 END) AS tsunami_count
        FROM earthquakes GROUP BY year ORDER BY year
    """,
    "20. Earthquake count by alert level (red, orange, etc.)": """
        SELECT alert, COUNT(*) AS earthquake_count
        FROM earthquakes WHERE alert IS NOT NULL AND TRIM(alert) <> ''
        GROUP BY alert ORDER BY earthquake_count DESC
    """,
    "21. Top 5 countries by average magnitude in the past 5 years": """
        SELECT country, ROUND(AVG(mag), 2) AS average_magnitude,
               COUNT(*) AS earthquake_count
        FROM earthquakes
        WHERE `time` >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
          AND country IS NOT NULL AND TRIM(country) <> '' AND mag IS NOT NULL
        GROUP BY country ORDER BY average_magnitude DESC LIMIT 5
    """,
     "22. Countries with shallow and deep earthquakes in the same month": """
        SELECT country, year, month,
               SUM(CASE WHEN depth_category = 'Shallow' THEN 1 ELSE 0 END) AS shallow_count,
               SUM(CASE WHEN depth_category = 'Deep' THEN 1 ELSE 0 END) AS deep_count
        FROM earthquakes WHERE country IS NOT NULL AND TRIM(country) <> ''
        GROUP BY country, year, month
        HAVING shallow_count > 0 AND deep_count > 0
        ORDER BY year, month, country
    """,
    "23. Year-over-year growth in global earthquake counts": """
        SELECT year, earthquake_count,
               LAG(earthquake_count) OVER (ORDER BY year) AS previous_year_count,
               ROUND(100.0 * (earthquake_count -
                   LAG(earthquake_count) OVER (ORDER BY year)) /
                   NULLIF(LAG(earthquake_count) OVER (ORDER BY year), 0), 2)
                   AS growth_rate_percent
        FROM (
            SELECT year, COUNT(*) AS earthquake_count
            FROM earthquakes GROUP BY year
        ) AS yearly_counts
        ORDER BY year
    """,
     "24. Top 3 regions by frequency and average magnitude": """
        SELECT country AS region, COUNT(*) AS earthquake_count,
               ROUND(AVG(mag), 2) AS average_magnitude
        FROM earthquakes WHERE country IS NOT NULL AND TRIM(country) <> ''
        GROUP BY country
        ORDER BY earthquake_count DESC, average_magnitude DESC LIMIT 3
    """,
    "25. Average depth by country near the equator (±5° latitude)": """
        SELECT country, ROUND(AVG(depth_km), 2) AS average_depth_km
        FROM earthquakes
        WHERE latitude BETWEEN -5 AND 5
          AND country IS NOT NULL AND TRIM(country) <> ''
        GROUP BY country ORDER BY average_depth_km DESC
    """,
    "26. Top 5 countries by shallow-to-deep earthquake ratio": """
        SELECT country,
               SUM(depth_category = 'Shallow') AS shallow_count,
               SUM(depth_category = 'Deep') AS deep_count,
               ROUND(SUM(depth_category = 'Shallow') /
                     NULLIF(SUM(depth_category = 'Deep'), 0), 2)
                     AS shallow_deep_ratio
        FROM earthquakes WHERE country IS NOT NULL AND TRIM(country) <> ''
        GROUP BY country HAVING deep_count > 0
        ORDER BY shallow_deep_ratio DESC LIMIT 5
    """,
    "27. Average magnitude difference: tsunami vs no tsunami": """
        SELECT ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END), 2) AS tsunami_avg_mag,
               ROUND(AVG(CASE WHEN tsunami = 0 THEN mag END), 2) AS no_tsunami_avg_mag,
               ROUND(AVG(CASE WHEN tsunami = 1 THEN mag END) -
                     AVG(CASE WHEN tsunami = 0 THEN mag END), 2)
                     AS average_magnitude_difference
        FROM earthquakes
    """,
    "28. Events with low data reliability (high gap and rms)": """
        SELECT id, `time`, place, mag, gap, rms
        FROM earthquakes
        WHERE gap > (SELECT AVG(gap) FROM earthquakes)
          AND rms > (SELECT AVG(rms) FROM earthquakes)
        ORDER BY gap DESC, rms DESC LIMIT 10
    """,
    "30. Regions with the most deep-focus earthquakes (> 300 km)": """
        SELECT country AS region, COUNT(*) AS deep_earthquake_count
        FROM earthquakes
        WHERE depth_km > 300 AND country IS NOT NULL AND TRIM(country) <> ''
        GROUP BY country ORDER BY deep_earthquake_count DESC LIMIT 10
    """,
}

st.header("Run Analysis")
selected_query = st.selectbox("Choose a question", list(queries.keys()))

if st.button("Run query", type="primary"):
    try:
        result = pd.read_sql(queries[selected_query], con=engine)
        st.subheader(selected_query)
        if result.empty:
            st.info("This query returned no rows.")
        else:
            st.dataframe(result, use_container_width=True)
    except Exception as error:
        st.error(f"Query failed: {error}")

st.caption(
    "Question 4,12,17,29 are not implemented."
)