import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# Database connection
def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='12345678',
            database='police_log',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None

# Fetch data from database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()

# Streamlit UI
st.set_page_config(page_title="SecureCheck Police Dashboard", layout="centered")

st.title("🚨 SecureCheck: Police Check Post Digital Ledger 🚨")
st.markdown("Real-time monitoring and insights for law enforcement 🚓")

# Show full table
st.header("📋 Police Logs Overview 📋")
query = "SELECT * FROM police_log"
data = fetch_data(query)
st.dataframe(data, use_container_width=True)

# Quick Metrics
st.header("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest", case=False, na=False)].shape[0]
    st.metric("Total Arrests", arrests)

with col3:
    warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)

with col4:
    drug_related = data[data['drugs_related_stop'] == 1].shape[0]
    st.metric("Drug Related Stops", drug_related)

# Charts
st.header("📈 Visual Insights 📈")

tab1, tab2 = st.tabs(["Stops by Violation", "Driver Gender Distribution"])

with tab1:
    if not data.empty and 'violation' in data.columns:
        violation_data = data['violation'].value_counts().reset_index()
        violation_data.columns = ['Violation', 'Count']
        fig = px.bar(violation_data, x='Violation', y='Count', title="Stops by Violation Type", color='Violation')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Violation chart.")

with tab2:
    if not data.empty and 'driver_gender' in data.columns:
        gender_data = data['driver_gender'].value_counts().reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig = px.pie(gender_data, names='Gender', values='Count', title="Driver Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Driver Gender chart.")

# Advanced Queries
st.header("🧩 Medium Level Insights 🧩")

selected_query = st.selectbox("Select a Query to Run", [
    "Total Number of Police Stops",
    "Count of Stops by Violation Type",
    "Number of Arrests vs. Warnings",
    "Average Age of Drivers Stopped",
    "Top 5 Most Frequent Search Types",
    "Count of Stops by Gender",
    "Most Common Violation for Arrests",
    "Average Stop Duration for Each Violation",
    "Number of Drug-Related Stops by Year",
    "Drivers with the Highest Number of Stops",
    "Number of Stops Conducted at Night (Between 10 PM - 5 AM)",
    "Number of Searches Conducted by Violation Type",
    "Arrest Rate by Driver Gender",
    "Violation Trends Over Time",
    "Most Common Stop Outcomes for Drug-Related Stops"
])

query_map = {
    "Total Number of Police Stops": "SELECT COUNT(*) AS total_police_stops FROM police_log",
    "Count of Stops by Violation Type": "SELECT violation, COUNT(*) AS stops_count FROM police_log GROUP BY violation",
    "Number of Arrests vs. Warnings": "SELECT stop_outcome, COUNT(*) AS outcome_count FROM police_log WHERE stop_outcome IN ('Arrest','Warning') GROUP BY stop_outcome",
    "Average Age of Drivers Stopped": "SELECT AVG(driver_age) AS avg_driver_age FROM police_log WHERE driver_age IS NOT NULL",
    "Top 5 Most Frequent Search Types": "SELECT search_type, COUNT(*) AS search_count FROM police_log WHERE search_type IS NOT NULL GROUP BY search_type LIMIT 5",
    "Count of Stops by Gender": "SELECT driver_gender, COUNT(*) AS stop_count FROM police_log GROUP BY driver_gender",
    "Most Common Violation for Arrests": "SELECT violation, COUNT(*) AS arrest_count FROM police_log WHERE is_arrested=TRUE GROUP BY violation LIMIT 1",
    "Average Stop Duration for Each Violation": "SELECT violation, stop_duration, COUNT(*) AS count FROM police_log GROUP BY violation, stop_duration",
    "Number of Drug-Related Stops by Year": "SELECT EXTRACT(YEAR FROM stop_date) AS year, COUNT(*) AS drugs_related_count FROM police_log WHERE drugs_related_stop=TRUE GROUP BY year",
    "Drivers with the Highest Number of Stops": "SELECT vehicle_number, COUNT(*) AS count_stop FROM police_log GROUP BY vehicle_number ORDER BY count_stop DESC LIMIT 5",
    "Number of Stops Conducted at Night (Between 10 PM - 5 AM)": "SELECT COUNT(*) AS night_stops FROM police_log WHERE (CAST(SUBSTR(stop_time, 1, 2) AS SIGNED) >= 22 OR CAST(SUBSTR(stop_time, 1, 2) AS SIGNED) < 5)",
    "Number of Searches Conducted by Violation Type": "SELECT violation, COUNT(*) AS searches_conducted FROM police_log WHERE search_conducted = TRUE GROUP BY violation",
    "Arrest Rate by Driver Gender": "SELECT driver_gender, COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) AS arrests_count, COUNT(*) AS total_stops, (COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) * 100.0 / COUNT(*)) AS arrest_rate_percentage FROM police_log GROUP BY driver_gender",
    "Violation Trends Over Time": "SELECT EXTRACT(YEAR FROM stop_date) AS year, EXTRACT(MONTH FROM stop_date) AS month, violation, COUNT(*) AS violation_count FROM police_log GROUP BY year, month, violation",
    "Most Common Stop Outcomes for Drug-Related Stops": "SELECT stop_outcome, COUNT(*) AS outcome_count FROM police_log WHERE drugs_related_stop=TRUE GROUP BY stop_outcome"
}

if st.button("Run Query"):
    result = fetch_data(query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("No results found for the selected query.")

st.header("🧩 Complex Level Insights 🧩")

your_query = st.selectbox("Select a Query to Run", [
    "Yearly Breakdown of Stops and Arrests by Country",
    "Driver Violation Trends Based on Age and Race",
    "Time Period Analysis of Stops",
    "Violations with High Search and Arrest Rates",
    "Driver Demographics by Country",
    "Top 5 Violations with Highest Arrest Rates"
])

your_query_map = {
    "Yearly Breakdown of Stops and Arrests by Country": "WITH stops_data AS ( SELECT country_name,EXTRACT(YEAR FROM stop_date) AS stop_year,COUNT(*) AS total_stops,SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests FROM police_log GROUP BY country_name, EXTRACT(YEAR FROM stop_date))SELECT * FROM stops_data",
    "Driver Violation Trends Based on Age and Race": "SELECT CASE  WHEN driver_age BETWEEN 16 AND 25 THEN '16-25' WHEN driver_age BETWEEN 26 AND 35 THEN '26-35' WHEN driver_age BETWEEN 36 AND 50 THEN '36-50' WHEN driver_age > 50 THEN '51+' ELSE 'Unknown' END AS age_group,driver_race,violation,COUNT(*) AS total_violations FROM police_log WHERE driver_age IS NOT NULL AND driver_race IS NOT NULL AND violation IS NOT NULL GROUP BY age_group, driver_race, violation ORDER BY age_group, driver_race, total_violations DESC",
    "Time Period Analysis of Stops": "WITH time_periods AS (SELECT stop_date,stop_time,CASE  WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 5 AND 11 THEN 'Morning' WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 12 AND 16 THEN 'Afternoon' WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 17 AND 20 THEN 'Evening' WHEN EXTRACT(HOUR FROM stop_time) BETWEEN 21 AND 23 THEN 'Night' ELSE 'Late Night' END AS time_period FROM police_log)Main query: count stops by date and time period SELECT DATE(stop_date) AS stop_day,time_period,COUNT(*) AS total_stops FROM time_periods GROUP BY DATE(stop_date), time_period ORDER BY stop_day, time_period",
    "Violations with High Search and Arrest Rates": "WITH violation_stats AS (SELECT violation,COUNT(*) AS total_stops,SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS total_searches,SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests FROM police_log WHERE violation IS NOT NULL GROUP BY violation)SELECT violation,total_stops,total_searches,total_arrests,ROUND((total_searches * 100.0) / total_stops, 2) AS search_rate_percent,ROUND((total_arrests * 100.0) / total_stops, 2) AS arrest_rate_percent,RANK() OVER (ORDER BY (total_searches * 1.0 / total_stops) DESC) AS search_rank,RANK() OVER (ORDER BY (total_arrests * 1.0 / total_stops) DESC) AS arrest_rank FROM violation_stats ORDER BY search_rate_percent DESC, arrest_rate_percent DESC",
    "Driver Demographics by Country": "SELECTcountry_name,driver_gender,driver_race,ROUND(AVG(driver_age), 1) AS average_age,COUNT(*) AS total_drivers FROM police_logWHERE driver_age IS NOT NULL AND driver_gender IS NOT NULL AND driver_race IS NOT NULL AND country_name IS NOT NULL GROUP BY country_name, driver_gender, driver_race ORDER BY country_name, total_drivers DESC",
    "Top 5 Violations with Highest Arrest Rates": "WITH violation_arrest_rate AS (SELECT violation,COUNT(*) AS total_stops,SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests, ROUND((SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) * 100.0) / COUNT(*), 2) AS arrest_rate_percent FROM police_log WHERE violation IS NOT NULL GROUP BY violation)SELECT violation,total_stops,total_arrests,arrest_rate_percent FROM violation_arrest_rate ORDER BY arrest_rate_percent DESC LIMIT 5"
}

if st.button("Run Your Query"):
    results = fetch_data(your_query_map[your_query])
    if not results.empty:
        st.write(results)
    else:
        st.warning("No results found for the selected query.")

st.markdown("---")
st.markdown("Built with ❤️ for Law Enforcement by SecureCheck")
st.header("🔍 Custom Natural Language Filter")


st.markdown("Fill in the details below to get a natural language prediction of the stop outcome based on existing data.")



st.header("📝 Add New Police Log & Predict Outcome and Violation")

# Input form for all fields (excluding outputs)
with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    county_name = st.text_input("County Name")
    driver_gender = st.selectbox("Driver Gender", ["male", "female"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was a Search Conducted?", ["0", "1"])
    search_type = st.text_input("Search Type")
    drugs_related_stop = st.selectbox("Was it Drug Related?", ["0", "1"])
    stop_duration = st.selectbox("Stop Duration", data['stop_duration'].dropna().unique())
    vehicle_number = st.text_input("Vehicle Number")
    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    if submitted:
        # Filter data for prediction
        filtered_data = data[
            (data['driver_gender'] == driver_gender) &
            (data['driver_age'] == driver_age) &
            (data['search_conducted'] == int(search_conducted)) &
            (data['stop_duration'] == stop_duration) &
            (data['drugs_related_stop'] == int(drugs_related_stop))
        ]

        # Predict stop_outcome
        if not filtered_data.empty:
            predicted_outcome = filtered_data['stop_outcome'].mode()[0]
            predicted_violation = filtered_data['violation'].mode()[0]
        else:
            predicted_outcome = "warning" 
            predicted_violation = "speeding"
        search_text = "A search was conducted" if int(search_conducted) else "No search was conducted"
        drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"
        st.markdown(f"""
        {predicted_violation}
        {predicted_outcome}
        🗒️ A {driver_age}-year-old {driver_gender} driver in {county_name} was stopped at {stop_time.strftime('%I:%M %p')} on {stop_date}.  
        {search_text}, and the stop {drug_text}.  
        {stop_duration}
        {vehicle_number}.
        """)
        
        