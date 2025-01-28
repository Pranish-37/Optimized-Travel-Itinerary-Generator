import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA
from pymongo import MongoClient
from datetime import timedelta
import seaborn as sns

# Set Page Configuration
st.set_page_config(
    page_title="Optimized Travel Itinerary",
    page_icon="🗺",
    layout="wide",
)

# CSS for Styling
page_bg = """
<style>
    body {
        background-image: url("https://images.unsplash.com/photo-1507525428034-b723cf961d3e");
        background-size: cover;
        background-attachment: fixed;
        color: white;
    }
    .centered-heading {
        text-align: center;
        font-size: 36px;
        font-weight: bold;
        margin-top: 20px;
        color: #ffffff;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.6);
    }
    .sidebar .sidebar-content {
        background: rgba(0, 0, 0, 0.7);
    }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# Sidebar Navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["Travel Plan", "Statistics & Graphs", "AQI Rankings"]
)

# State Name Dropdown
state_name_to_abbr = {
   "Andhra Pradesh": "AP",
    "Arunachal Pradesh": "AR",
    "Assam": "AS",
    "Bihar": "BR",
    "Chhattisgarh": "CG",
    "Goa": "GA",
    "Gujarat": "GJ",
    "Haryana": "HR",
    "Himachal Pradesh": "HP",
    "Jharkhand": "JH",
    "Karnataka": "KA",
    "Kerala": "KL",
    "Madhya Pradesh": "MP",
    "Maharashtra": "MH",
    "Manipur": "MN",
    "Meghalaya": "ML",
    "Mizoram": "MZ",
    "Nagaland": "NL",
    "Odisha": "OD",
    "Punjab": "PB",
    "Rajasthan": "RJ",
    "Sikkim": "SK",
    "Tamil Nadu": "TN",
    "Telangana": "TG",
    "Tripura": "TR",
    "Uttar Pradesh": "UP",
    "Uttarakhand": "UK",
    "West Bengal": "WB",
    "Andaman and Nicobar Islands": "AN",
    "Chandigarh": "CH",
    "Dadra and Nagar Haveli and Daman and Diu": "DN",
    "Delhi": "DL",
    "Jammu and Kashmir": "JK",
    "Ladakh": "LA",
    "Lakshadweep": "LD",
    "Puducherry": "PY"
}
state_name = st.sidebar.selectbox("Select a State", list(state_name_to_abbr.keys()))
state_abbr = state_name_to_abbr[state_name]

# User Inputs
forecast_days = st.sidebar.slider("Number of Forecast Days", 1, 10, 5)
rerun = st.sidebar.button("Re-run Analysis")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")  # Adjust with your MongoDB URI
db = client["Orproj"]  # Replace with your database name
aqi_collection = db["aqi data"]  # Replace with your AQI collection name
stations_collection = db["dataset"]  # Replace with your stations collection name

   

# Fetch Station Details from MongoDB (Including PlaceName)
stations_data = pd.DataFrame(list(stations_collection.find({"StationId": {"$regex": f"^{state_abbr}"}})))

# Validate if stations are available
if stations_data.empty:
    st.error(f"No stations found for the state: {state_name}")
    st.stop()

# Fetch AQI Data from MongoDB
data = pd.DataFrame(list(aqi_collection.find({"StationId": {"$in": stations_data['StationId'].tolist()}})))
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data = data.dropna(subset=['AQI'])
data['AQI'] = pd.to_numeric(data['AQI'], errors='coerce')

# Train ARIMA and Predict AQI
@st.cache_data
def train_arima_and_predict(data, stations_data, forecast_days):
    state_forecasts = {}
    for station in stations_data['StationId']:
        station_data = data[data['StationId'] == station]
        if station_data.empty:
            state_forecasts[station] = [np.nan] * forecast_days
            continue
        try:
            series = station_data['AQI']
            model = ARIMA(series, order=(1, 1, 1))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=forecast_days)
            state_forecasts[station] = forecast.tolist()
        except Exception as e:
            st.warning(f"ARIMA failed for station {station}: {e}")
            state_forecasts[station] = [np.nan] * forecast_days
    return state_forecasts

state_forecasts = train_arima_and_predict(data, stations_data, forecast_days)
stations_data['AQI'] = stations_data['StationId'].apply(lambda x: state_forecasts[x][0] if state_forecasts[x] else np.nan)

# Sorting the stations based on the AQI for the current day
sorted_stations = stations_data.sort_values(by="AQI", ascending=True)

# Compute Distance Matrix
@st.cache_data
def compute_distance_matrix(stations):
    n = len(stations)
    distance_matrix = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                coord1 = (stations.iloc[i]['Latitude'], stations.iloc[i]['Longitude'])
                coord2 = (stations.iloc[j]['Latitude'], stations.iloc[j]['Longitude'])
                distance_matrix[i][j] = geodesic(coord1, coord2).km
    return distance_matrix

distance_matrix = compute_distance_matrix(stations_data)

# Compute Optimized Travel Plan
@st.cache_data
def find_optimized_plan(stations, state_forecasts, distance_matrix, forecast_days):
    n = len(stations)
    visited = set()
    plan = []
    current_station = 0
    for day in range(forecast_days):
        visited.add(current_station)
        next_station = np.argmin(
            [state_forecasts[stations.iloc[j]['StationId']][day] + distance_matrix[current_station][j]
             if j not in visited else float('inf') for j in range(n)]
        )
        travel_distance = distance_matrix[current_station][next_station]
        travel_time = travel_distance / 50
        plan.append({
            "Current Station": stations.iloc[current_station]['Place'] if day > 0 else None,
            "Next Station": stations.iloc[next_station]['Place'],
            "Day": day + 1,
            "Distance (km)": travel_distance if day > 0 else None,
            "Travel Time (hours)": travel_time if day > 0 else None
        })
        current_station = next_station
    return plan

optimized_plan = find_optimized_plan(stations_data, state_forecasts, distance_matrix, forecast_days)

# Visualization: Folium Map
def create_folium_map():
    start_location = [stations_data.iloc[0]['Latitude'], stations_data.iloc[0]['Longitude']]
    travel_map = folium.Map(location=start_location, zoom_start=8)
    for _, row in stations_data.iterrows():
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            popup=(f"<b>Place Name:</b> {row['Place']}<br><b>AQI:</b> {row['AQI']}"),
            icon=folium.Icon(color="blue", icon="info-sign"),
        ).add_to(travel_map)
    for i, entry in enumerate(optimized_plan):
        if i > 0:
            prev_station = entry["Current Station"]
            next_station = entry["Next Station"]
            prev_coords = stations_data[stations_data['Place'] == prev_station].iloc[0]
            next_coords = stations_data[stations_data['Place'] == next_station].iloc[0]
            folium.PolyLine(
                locations=[ [prev_coords['Latitude'], prev_coords['Longitude']], [next_coords['Latitude'], next_coords['Longitude']] ],
                color="red", weight=2.5, opacity=1
            ).add_to(travel_map)
    return travel_map

# Page: AQI Rankings
if page == "AQI Rankings":
    st.markdown("<h1 class='centered-heading'>📊 AQI Rankings</h1>", unsafe_allow_html=True)
    st.write(f"### AQI Rankings for Places in {state_name}:")
    for idx, row in sorted_stations.iterrows():
        st.write(f"*Place Name: {row['Place']} - **AQI*: {row['AQI']}")

# Page: Travel Plan
elif page == "Travel Plan":
    st.markdown("<h1 class='centered-heading'>🌍 Optimized Travel Itinerary</h1>", unsafe_allow_html=True)
    st.write(f"### Optimized Travel Plan for {state_name}:")
    for entry in optimized_plan:
        if entry["Current Station"] is None:
            st.write(f"Day {entry['Day']}: Start your journey at Place {entry['Next Station']}.")
        else:
            st.write(
                f"Day {entry['Day']}: Spend the day exploring Place {entry['Current Station']}, "
                f"and travel at night to Place {entry['Next Station']}.\n"
                f"    Distance: {entry['Distance (km)']:.2f} km, Travel Time: {entry['Travel Time (hours)']:.2f} hours."
            )
    st.write("### Interactive Map")
    travel_map = create_folium_map()
    st_folium(travel_map, width=800, height=500)


    
# Fetch data from MongoDB
aqi_data = pd.DataFrame(list(aqi_collection.find()))
stations_data = pd.DataFrame(list(stations_collection.find()))

# Preprocess AQI data
if 'Date' in aqi_data.columns:
    aqi_data['Date'] = pd.to_datetime(aqi_data['Date'], errors='coerce')  # Convert to datetime
if 'AQI' in aqi_data.columns:
    aqi_data = aqi_data.dropna(subset=['AQI'])                           # Drop rows with NaN AQI

if 'StationId' in aqi_data.columns:
    aqi_data['State'] = aqi_data['StationId'].str[:2]                    # Extract state abbreviation

aqi_data['Month'] = aqi_data['Date'].dt.month                           # Add a 'Month' column




if page == "Statistics & Graphs":
    st.markdown("<h1 class='centered-heading'>📊 Statistics and Graphs</h1>", unsafe_allow_html=True)

    ### 1. High AQI Months for a Given State
    if 'State' in aqi_data.columns:
        state_abbr = st.sidebar.selectbox("Select State Abbreviation", aqi_data['State'].unique())
        state_data = aqi_data[aqi_data['State'] == state_abbr]

        # Monthly AQI averages for the given state
        monthly_avg_aqi = state_data.groupby('Month')['AQI'].mean()

        # Identify the month(s) with the highest AQI
        max_aqi_months = monthly_avg_aqi[monthly_avg_aqi == monthly_avg_aqi.max()]
        st.write(f"### High AQI Months for State: {state_abbr}")
        st.write(max_aqi_months)

        # Visualization for High AQI Months
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        monthly_avg_aqi.plot(kind='bar', color='orange', edgecolor='black', ax=ax1)
        ax1.set_title(f"Monthly Average AQI for State {state_abbr}")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Average AQI")
        ax1.set_xticks(range(12))
        ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
        ax1.axhline(monthly_avg_aqi.max(), color='red', linestyle='--', label='Highest AQI Month(s)')
        ax1.legend()
        st.pyplot(fig1)

    ### 2. State with the Highest AQI
    if 'State' in aqi_data.columns:
        # Aggregate AQI by state
        state_avg_aqi = aqi_data.groupby('State')['AQI'].mean()

        # Find the state with the highest AQI
        highest_aqi_state = state_avg_aqi.idxmax()
        highest_aqi_value = state_avg_aqi.max()
        st.write(f"### State with the Highest AQI")
        st.write(f"The state with the highest AQI is *{highest_aqi_state}* with an average AQI of *{highest_aqi_value:.2f}*.")

        # Visualization for State with the Highest AQI
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        state_avg_aqi.sort_values().plot(kind='bar', color='skyblue', edgecolor='black', ax=ax2)
        ax2.set_title("Average AQI by State")
        ax2.set_xlabel("State")
        ax2.set_ylabel("Average AQI")
        ax2.axhline(highest_aqi_value, color='red', linestyle='--', label=f'Highest AQI: {highest_aqi_state}')
        ax2.legend()
        st.pyplot(fig2)