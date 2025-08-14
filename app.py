import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="Ola Ride Insights Dashboard", layout="wide")

# Load dataset
def load_data():
    df = pd.read_excel("OLA_DataSet.xlsx", sheet_name="July")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

# Create SQLite in-memory DB for SQL queries
conn = sqlite3.connect(":memory:")
df.to_sql("rides", conn, index=False, if_exists="replace")

# Sidebar filters
st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", df['Date'].min())
end_date = st.sidebar.date_input("End Date", df['Date'].max())
vehicle_filter = st.sidebar.multiselect("Vehicle Type", options=df['Vehicle_Type'].unique(), default=df['Vehicle_Type'].unique())
payment_filter = st.sidebar.multiselect("Payment Method", options=df['Payment_Method'].dropna().unique(), default=df['Payment_Method'].dropna().unique())

# Apply filters
mask = (
    (df['Date'] >= pd.to_datetime(start_date)) &
    (df['Date'] <= pd.to_datetime(end_date)) &
    (df['Vehicle_Type'].isin(vehicle_filter)) &
    (df['Payment_Method'].isin(payment_filter))
)
df_filtered = df[mask]

# Tabs
tabs = st.tabs(["Overview", "Vehicle Insights", "Revenue", "Cancellations", "Ratings"])

# ------------------ Overview Tab ------------------
with tabs[0]:
    st.subheader("Ride Volume Over Time")
    rides_per_day = df_filtered.groupby('Date').size()
    fig, ax = plt.subplots()
    rides_per_day.plot(kind='line', ax=ax)
    ax.set_ylabel("Number of Rides")
    st.pyplot(fig)

    st.subheader("Booking Status Breakdown")
    status_counts = df_filtered['Booking_Status'].value_counts()
    fig, ax = plt.subplots()
    status_counts.plot(kind='bar', ax=ax)
    ax.set_ylabel("Count")
    st.pyplot(fig)

# ------------------ Vehicle Insights Tab ------------------
with tabs[1]:
    st.subheader("Top 5 Vehicle Types by Ride Distance")
    top_vehicle = df_filtered.groupby('Vehicle_Type')['Ride_Distance'].sum().sort_values(ascending=False).head(5)
    fig, ax = plt.subplots()
    top_vehicle.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# ------------------ Revenue Tab ------------------
with tabs[2]:
    st.subheader("Revenue by Payment Method")
    rev_payment = df_filtered.groupby('Payment_Method')['Booking_Value'].sum()
    fig, ax = plt.subplots()
    rev_payment.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.subheader("Top 5 Customers by Total Booking Value")
    top_customers = df_filtered.groupby('Customer_ID')['Booking_Value'].sum().sort_values(ascending=False).head(5)
    fig, ax = plt.subplots()
    top_customers.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# ------------------ Cancellations Tab ------------------
with tabs[3]:
    st.subheader("Cancelled Rides by Customer Reason")
    cust_cancel = df_filtered['Canceled_Rides_by_Customer'].value_counts().head(10)
    fig, ax = plt.subplots()
    cust_cancel.plot(kind='bar', ax=ax)
    st.pyplot(fig)

    st.subheader("Cancelled Rides by Driver Reason")
    driver_cancel = df_filtered['Canceled_Rides_by_Driver'].value_counts().head(10)
    fig, ax = plt.subplots()
    driver_cancel.plot(kind='bar', ax=ax)
    st.pyplot(fig)

# ------------------ Ratings Tab ------------------
with tabs[4]:
    st.subheader("Driver Ratings Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df_filtered['Driver_Ratings'].dropna(), kde=True, ax=ax)
    st.pyplot(fig)

    st.subheader("Customer Ratings Distribution")
    fig, ax = plt.subplots()
    sns.histplot(df_filtered['Customer_Rating'].dropna(), kde=True, ax=ax)
    st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.info("Ola Ride Insights Dashboard - Streamlit App")
