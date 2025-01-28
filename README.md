# Optimized Travel Itinerary Generator

### 🌍 Travel Smartly While Considering Air Quality

This project introduces an **Optimized Travel Itinerary Generator** that incorporates **real-time Air Quality Index (AQI) data** and **advanced forecasting techniques** to create the healthiest and most efficient travel plans. It minimizes exposure to air pollution, optimizes travel routes, and maximizes leisure time for a better travel experience.

---

## 📌 Problem Statement
Travel planning involves balancing multiple factors like:
- Destination preferences.
- Travel duration and route efficiency.
- **Air Quality**, a growing concern due to rising pollution levels.

This project solves challenges like:
1. **Unpredictable AQI Levels**: Identifies the best travel days with low pollution.
2. **Excessive Travel**: Reduces travel distance and time between destinations.
3. **Lack of Data-Driven Decisions**: Uses statistical analysis and forecasting to guide travel plans.

---

## ✨ Key Features
1. **Dynamic AQI Forecasting**:  
   Utilizes **ARIMA (AutoRegressive Integrated Moving Average)** for predicting AQI trends across multiple locations.  
   - Forecasts pollution levels over **n future days**.
   - Enables travelers to avoid high-AQI days at specific destinations.

2. **Optimized Travel Plans**:  
   - Integrates **geospatial mapping** and **distance matrix optimization**.
   - Custom **Greedy Optimization Algorithm** balances **AQI** and **travel distance**.

3. **Geospatial Visualizations**:  
   - **Interactive maps** using Folium.
   - **Station rankings** and optimized travel routes are dynamically visualized.

4. **Statistical Analysis**:  
   - **Seasonal AQI trends** to identify high-pollution months for each state.
   - **Statewise AQI rankings** to highlight critical areas for travelers.

---

## 📊 Statistical Analysis
1. **High AQI Months for a State**:  
   Bar chart analysis showing the months with the highest AQI levels for a given state, enabling seasonal travel planning.  

2. **State with the Highest AQI**:  
   Comparative analysis across states to identify the most polluted regions, visualized through interactive bar charts.

   **You can see samples pictures in images folder.**
---

## 🔧 Methodology
- **ARIMA Forecasting**:  
  Captures temporal AQI trends for accurate predictions.  
  Formula:  
  \[
  AQI(t) = AR(t) + I(t) + MA(t)
  \]  

- **Travel Optimization**:  
  Combines forecasted AQI and geodesic distances between cities to dynamically compute an efficient itinerary.  
  Cost Function:  
  \[
  \text{Cost} = \text{Predicted AQI} + \text{Travel Distance}
  \]

---

## 📁 Dataset
1. **Time Series Air Quality Data of India (2015-2020)**  
   - Source: Kaggle.  
   - Includes parameters like **PM2.5, PM10, NO2**, and more.

2. **Station Coordinates**  
   - Geospatial data for mapping and route optimization.

---

## ⚙️ Technologies Used
- **Programming**: Python, Streamlit.  
- **Visualization**: Folium, Matplotlib, Seaborn.  
- **Forecasting**: Statsmodels (ARIMA).  
- **Database**: MongoDB for AQI and geospatial data.  
- **Optimization**: NumPy, Geopy.  

---

## 🔗 How It Works
1. **Step 1**: Load AQI and station data from MongoDB.  
2. **Step 2**: Forecast AQI for each station using ARIMA.  
3. **Step 3**: Compute distance matrix using **geodesic distances**.  
4. **Step 4**: Optimize travel plan with **dynamic AQI predictions** and travel constraints.  
5. **Step 5**: Visualize results with interactive maps and graphs.

---

## 📋 Results
- Optimized travel itineraries for low AQI exposure.
- Dynamic route mapping with pollution-aware planning.
- Interactive visualizations for enhanced decision-making.

---

## 🚀 Installation
1. Clone this repository:  
   ```bash
   git clone https://github.com/Pranish-37/Optimized-Travel-Itinerary
   cd Optimized-Travel-Itinerary
   ```

2. Install dependencies:  
  Install dependecies and put all these files together in a folder

3. Start the Streamlit app:  
   ```bash
   streamlit run OR_Project1.py
   ```

---

## 🌟 Future Scope
1. Incorporate real-time weather and traffic data.  
2. Implement machine learning models for route prediction.  
3. Develop mobile and web-based applications.

---

Let us know if you'd like to contribute or have feedback!




