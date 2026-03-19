import streamlit as st
import pandas as pd
import requests
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(page_title="EIA Energy Dashboard", layout="wide")

# EIA API setup
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_eia_data(frequency='monthly', state='US', sector='RES', data_types=['sales', 'revenue', 'price']):
    api_key = st.secrets.get("EIA_API_KEY")
    if not api_key:
        st.error("Set EIA_API_KEY in Hugging Face Spaces secrets.")
        return None
    
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    
    facets = {'stateid': [state], 'sectorid': [sector]}
    params_dict = {
        'frequency': frequency,
        'data': data_types,
        'facets': facets,
        'start': '2020-01',  # Adjust as needed
        'end': datetime.now().strftime('%Y-%m'),
        'sort': [{'column': {'name': 'period'}}, {'column': {'name': 'stateid'}}],
        'offset': 0,
        'length': 5000
    }
    
    params = {'api_key': api_key}
    headers = {'X-Params': json.dumps(params_dict)}
    
    try:
        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        
        if 'response' in data and 'data' in data['response']:
            df = pd.DataFrame(data['response']['data'])
            if not df.empty:
                df['period'] = pd.to_datetime(df['period'])
                df = df.pivot(index='period', columns='type', values='value').reset_index()
                df = df.dropna()
                return df.sort_values('period')
        st.warning("No data returned. Check facets or date range.")
        return None
    except Exception as e:
        st.error(f"API error: {str(e)}")
        return None

# Streamlit app
st.title("🛢️ EIA Electricity Retail Sales Dashboard")
st.markdown("Fetches live data on electricity sales, revenue, and prices. Focuses on residential (RES) by default.")

col1, col2, col3 = st.columns(3)
with col1:
    frequency = st.selectbox("Frequency", ['monthly', 'annual', 'quarterly'])
with col2:
    state = st.selectbox("State", ['US', 'DC', 'TX', 'CA', 'NY'])  # DC for your area
with col3:
    sector = st.selectbox("Sector", ['RES', 'IND', 'COM', 'TRA'])

if st.button("Fetch & Analyze Data", type="primary"):
    with st.spinner("Pinging EIA API..."):
        df = fetch_eia_data(frequency, state, sector)
    
    if df is not None:
        st.success(f"Loaded {len(df)} periods of data.")
        
        # Summary stats
        st.subheader("Summary Statistics")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.metric("Avg Sales (M kWh)", f"{df['sales'].mean():.1f}")
        with col_b:
            st.metric("Avg Price ($/kWh)", f"{df['price'].mean():.4f}")
        with col_c:
            st.metric("Total Revenue ($M)", f"{df['revenue'].sum():.0f}")
        
        stats_df = df[['sales', 'revenue', 'price']].describe().round(2)
        st.dataframe(stats_df)
        
        # Graphs
        st.subheader("Trends")
        fig_line = px.line(df, x='period', y=['sales', 'revenue', 'price'], 
                          title=f"{sector} Electricity Metrics - {state}")
        fig_line.update_yaxes(title="Value")
        st.plotly_chart(fig_line, use_container_width=True)
        
        fig_bar = px.bar(df, x='period', y='price', title="Price Over Time")
        st.plotly_chart(fig_bar, use_container_width=True)
        
        st.dataframe(df.tail(12), use_container_width=True)
    else:
        st.stop()
