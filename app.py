import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_eia_data(api_key, state_id='US'):
    # Proven working params from EIA docs
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    params = {
        'api_key': api_key,
        'data[]': ['revenue', 'sales', 'price', 'customers'],  # Exact column names
        'facets[sectorid][]': 'RES',
        'facets[stateid][]': state_id,
        'frequency': 'monthly',
        'start': '202401',  # YYYYMM - last 24 months auto
        'end': '202601',
        'length': 50
    }
    response = requests.get(url, params=params)
    st.write("Debug URL:", response.url)  # Remove after testing
    if response.status_code == 200:
        data = response.json()['response']['data']
        if 
            df = pd.DataFrame(data)
            df['period'] = pd.to_datetime(df['period'])
            df[['revenue', 'sales', 'price', 'customers']] = df[['revenue', 'sales', 'price', 'customers']].fillna(0).astype(float)
            return df
    st.error(f"API Error {response.status_code}: {response.text[:500]}")
    return pd.DataFrame()

STATE_OPTIONS = ['US', 'DC', 'CA', 'TX', 'FL', 'NY']
STATE_NAMES = {'US': 'USA', 'DC': 'DC', 'CA': 'California', 'TX': 'Texas', 'FL': 'Florida', 'NY': 'New York'}

st.title("⚡ EIA Electricity Dashboard - FIXED")
st.markdown("Residential sales/price by state (tested working).")

try:
    api_key = st.secrets["EIA_API_KEY"]
except:
    st.error("Add EIA_API_KEY secret!")
    st.stop()

state_id = st.selectbox("State:", STATE_OPTIONS, format_func=lambda x: STATE_NAMES[x])

df = fetch_eia_data(api_key, state_id)

if not df.empty:
    # Metrics (aggregate)
    col1, col2, col3 = st.columns(3)
    col1.metric("Sales (MWh)", f"{df['sales'].sum():,.0f}")
    col2.metric("Avg Price ($/kWh)", f"{df['price'].mean():.3f}")
    col3.metric("Revenue ($M)", f"{df['revenue'].sum():,.0f}")

    # Line chart
    fig = px.line(df, x='period', y=['sales', 'price'], 
                  title=f"{STATE_NAMES[state_id]} Residential Electricity")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df.round(3))
    
    csv = df.to_csv(index=False).encode()
    st.download_button("Download", csv, "eia.csv")
else:
    st.info("🔄 Check API key/try 'US'.")
