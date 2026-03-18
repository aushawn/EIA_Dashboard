import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.title("⚡ EIA Electricity Dashboard - FIXED")

# Secure API key
try:
    api_key = st.secrets["EIA_API_KEY"]
except:
    st.error("❌ Add EIA_API_KEY in secrets.toml or HF Space secrets!")
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
    st.write("Debug:", response.status_code, response.url)  # Remove after test
    
    **if response.status_code == 200 and response.json().get('response', {}).get('data'):**
        data = response.json()['response']['data']
        df = pd.DataFrame(data)
        if not df.empty:
            df['period'] = pd.to_datetime(df['period'])
            for col in ['revenue', 'sales', 'price', 'customers']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            return df
    
    st.error(f"API failed: {response.status_code} - {response.text[:200]}")
    return pd.DataFrame()

# States
STATE_OPTIONS = ['US', 'DC', 'CA', 'TX']
STATE_NAMES = {'US': 'USA', 'DC': 'DC', 'CA': 'California', 'TX': 'Texas'}

state_id = st.selectbox("State:", STATE_OPTIONS, format_func=lambda x: STATE_NAMES[x])

df = fetch_eia_data(api_key, state_id)

if not df.empty:
    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Sales (MWh)", f"{df['sales'].sum():,.0f}")
    col2.metric("Avg Price", f"{df['price'].mean():.3f} $/kWh")
    col3.metric("Revenue ($M)", f"{df['revenue'].sum():,.0f}")

    # Chart
    fig = px.line(df, x='period', y=['sales', 'price'], title=f"{STATE_NAMES[state_id]} Electricity")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df)
    st.download_button("Download CSV", df.to_csv(index=False).encode(), "eia.csv")
else:
    st.info("No data. Check API key (test 'US' first).")
