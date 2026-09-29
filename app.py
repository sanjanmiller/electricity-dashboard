import streamlit as st
import pandas as pd
import plotly.express as px


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Electricity Consumption Dashboard",
    page_icon="⚡",
    layout="wide"
)


# --------------------------------------------------
# Load data
# --------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv("electricity_consumption_dataset.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


df = load_data()


# --------------------------------------------------
# Data preparation
# --------------------------------------------------

df["date"] = df["timestamp"].dt.date
df["month"] = df["timestamp"].dt.to_period("M").astype(str)

# Remove rows where essential values are missing
df = df.dropna(
    subset=["timestamp", "electricity_consumption_kwh"]
)


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Filters")

cities = st.sidebar.multiselect(
    "City",
    options=sorted(df["city"].dropna().unique()),
    default=sorted(df["city"].dropna().unique())
)

building_types = st.sidebar.multiselect(
    "Building Type",
    options=sorted(df["building_type"].dropna().unique()),
    default=sorted(df["building_type"].dropna().unique())
)

seasons = st.sidebar.multiselect(
    "Season",
    options=sorted(df["season"].dropna().unique()),
    default=sorted(df["season"].dropna().unique())
)


filtered_df = df[
    (df["city"].isin(cities)) &
    (df["building_type"].isin(building_types)) &
    (df["season"].isin(seasons))
]


# --------------------------------------------------
# Title
# --------------------------------------------------

st.title("Electricity Consumption Analytics")

st.markdown(
    "Interactive analysis of electricity consumption, "
    "demand, weather, occupancy and solar generation."
)


# --------------------------------------------------
# KPI section
# --------------------------------------------------

total_consumption = filtered_df["electricity_consumption_kwh"].sum()

avg_consumption = filtered_df["electricity_consumption_kwh"].mean()

peak_demand = filtered_df["peak_demand_kw"].max()

total_solar = filtered_df["solar_generation_kwh"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Consumption",
    f"{total_consumption:,.0f} kWh"
)

col2.metric(
    "Average Consumption",
    f"{avg_consumption:.2f} kWh"
)

col3.metric(
    "Peak Demand",
    f"{peak_demand:.2f} kW"
)

col4.metric(
    "Solar Generation",
    f"{total_solar:,.0f} kWh"
)


st.divider()


# --------------------------------------------------
# Consumption over time
# --------------------------------------------------

st.subheader("Electricity Consumption Over Time")

daily_consumption = (
    filtered_df
    .groupby("date")["electricity_consumption_kwh"]
    .sum()
    .reset_index()
)

fig = px.line(
    daily_consumption,
    x="date",
    y="electricity_consumption_kwh",
    title="Daily Electricity Consumption",
    labels={
        "date": "Date",
        "electricity_consumption_kwh": "Consumption (kWh)"
    }
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Building type analysis
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    building_consumption = (
        filtered_df
        .groupby("building_type")["electricity_consumption_kwh"]
        .sum()
        .reset_index()
        .sort_values(
            "electricity_consumption_kwh",
            ascending=False
        )
    )

    fig = px.bar(
        building_consumption,
        x="building_type",
        y="electricity_consumption_kwh",
        title="Consumption by Building Type",
        labels={
            "building_type": "Building Type",
            "electricity_consumption_kwh": "Consumption (kWh)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# City analysis
# --------------------------------------------------

with col2:

    city_consumption = (
        filtered_df
        .groupby("city")["electricity_consumption_kwh"]
        .sum()
        .reset_index()
        .sort_values(
            "electricity_consumption_kwh",
            ascending=False
        )
    )

    fig = px.bar(
        city_consumption,
        x="city",
        y="electricity_consumption_kwh",
        title="Consumption by City",
        labels={
            "city": "City",
            "electricity_consumption_kwh": "Consumption (kWh)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Hourly consumption pattern
# --------------------------------------------------

st.subheader("Hourly Consumption Pattern")

hourly = (
    filtered_df
    .groupby("hour")["electricity_consumption_kwh"]
    .mean()
    .reset_index()
)

fig = px.line(
    hourly,
    x="hour",
    y="electricity_consumption_kwh",
    markers=True,
    title="Average Consumption by Hour",
    labels={
        "hour": "Hour of Day",
        "electricity_consumption_kwh": "Average Consumption (kWh)"
    }
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Temperature vs consumption
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.subheader("Temperature vs Consumption")

    fig = px.scatter(
        filtered_df.sample(
            min(5000, len(filtered_df)),
            random_state=42
        ),
        x="temperature_c",
        y="electricity_consumption_kwh",
        color="building_type",
        opacity=0.6,
        title="Temperature vs Electricity Consumption",
        labels={
            "temperature_c": "Temperature (°C)",
            "electricity_consumption_kwh": "Consumption (kWh)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Occupancy vs consumption
# --------------------------------------------------

with col2:

    st.subheader("Occupancy vs Consumption")

    fig = px.scatter(
        filtered_df.sample(
            min(5000, len(filtered_df)),
            random_state=42
        ),
        x="occupancy",
        y="electricity_consumption_kwh",
        color="building_type",
        opacity=0.6,
        title="Occupancy vs Electricity Consumption",
        labels={
            "occupancy": "Occupancy",
            "electricity_consumption_kwh": "Consumption (kWh)"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Solar vs consumption
# --------------------------------------------------

st.subheader("Solar Generation vs Electricity Consumption")

solar_daily = (
    filtered_df
    .groupby("date")[
        [
            "electricity_consumption_kwh",
            "solar_generation_kwh"
        ]
    ]
    .sum()
    .reset_index()
)

fig = px.line(
    solar_daily,
    x="date",
    y=[
        "electricity_consumption_kwh",
        "solar_generation_kwh"
    ],
    title="Daily Consumption vs Solar Generation",
    labels={
        "date": "Date",
        "value": "Energy (kWh)",
        "variable": "Metric"
    }
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Top energy-consuming buildings
# --------------------------------------------------

st.subheader("Top Energy-Consuming Buildings")

top_buildings = (
    filtered_df
    .groupby("building_id")["electricity_consumption_kwh"]
    .sum()
    .reset_index()
    .sort_values(
        "electricity_consumption_kwh",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top_buildings,
    x="electricity_consumption_kwh",
    y="building_id",
    orientation="h",
    title="Top 10 Buildings by Electricity Consumption",
    labels={
        "building_id": "Building",
        "electricity_consumption_kwh": "Consumption (kWh)"
    }
)

st.plotly_chart(fig, use_container_width=True)


# --------------------------------------------------
# Dataset preview
# --------------------------------------------------

with st.expander("View Dataset"):

    st.write(
        f"Showing {len(filtered_df):,} records"
    )

    st.dataframe(
        filtered_df,
        use_container_width=True
    )