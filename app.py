import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.title("EIA Electricity Dashboard")

try:
    api_key = st.secrets["EIA_API_KEY"]
except:
    st.error("Add EIA_API_KEY to .streamlit/secrets.toml")
    st.stop()

@st.cache_data(ttl=3600)
def fetch_eia_data(api_key, state_id='US'):
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    params = {
        'api_key': api_key,
        'data[]': ['revenue', 'sales', 'price', 'customers'],
        'facets[sectorid][]': 'RES',
        'facets[stateid][]': state_id,
        'frequency': 'monthly',
        'start': '202501',
        'length': 12
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()['response']['data']
        if data:
            df = pd.DataFrame(data)
            df['period'] = pd.to_datetime(df['period'])
            for col in ['revenue', 'sales', 'price', 'customers']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
    
    st.error(f"API Error {response.status_code}")
    return pd.DataFrame()

STATE_OPTIONS = ['US', 'DC']
STATE_NAMES = {'US': 'USA', 'DC': 'DC'}

state_id = st.selectbox("State:", STATE_OPTIONS, format_func=lambda x: STATE_NAMES[x])
df = fetch_eia_data(api_key, state_id)

if not df.empty:
    col1, col2 = st.columns(2)
    col1.metric("Sales MWh", f"{df['sales'].sum():,.0f}")
    col2.metric("Avg Price", f"{df['price'].mean():.3f} $/kWh")
    
    fig = px.line(df, x='period', y='price', title="Electricity Price")
    st.plotly_chart(fig)
    
    st.dataframe(df)
else:
    st.info("No data - check key")
