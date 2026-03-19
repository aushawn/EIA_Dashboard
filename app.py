import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from datetime import datetime, timedelta

@st.cache_data(ttl=3600)
def fetch_eia_data(api_key, start_date, end_date, state_id='US'):
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    params = {
        'api_key': api_key,
        'data[0]': 'value',  # Single data param (fixes 400)
        'facets[respondent][]': [],  # All respondents
        'facets[sectorid][]': ['RES'],  # Residential
        'facets[stateid][]': [state_id],  # Single state (multi fails)
        'facets[datatype][]': ['SALES', 'PRICE', 'REVENUE', 'CUSTOMERS'],  # Explicit
        'frequency': 'monthly',
        'start': start_date,  # YYYYMMDD no -
        'end': end_date,
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'offset': 0,
        'length': 500
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()['response']['data']
        if not data:
            return pd.DataFrame()
        df = pd.DataFrame(data)
        df['period'] = pd.to_datetime(df['period'].astype(str), format='%Y%m')
        numeric_cols = ['value']  # EIA v2 returns 'value' column
        df[numeric_cols] = df[numeric_cols].astype(float)
        df['datatype'] = df['datatype'].fillna('UNKNOWN')
        # Pivot to wide format
        df_wide = df.pivot(index=['period', 'respondent', 'stateDescription'], 
                          columns='datatype', values='value').reset_index()
        df_wide.columns.name = None
        return df_wide
    else:
        st.error(f"API {response.status_code}: {response.text[:300]}")
        return pd.DataFrame()

# States (EIA codes)
STATE_OPTIONS = ['US', 'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL']
STATE_NAMES = {'US': 'United States', 'DC': 'District of Columbia', 'CA': 'California', 'TX': 'Texas', 'FL': 'Florida'}  # Add more as needed

st.title("⚡ EIA Residential Electricity Dashboard")
st.markdown("Fixed API calls + state selector + US map.")

try:
    api_key = st.secrets["EIA_API_KEY"]
except:
    st.error("❌ Add EIA_API_KEY secret.")
    st.stop()

col1, col2 = st.columns(2)
with col1:
    state_id = st.selectbox("State/Region:", STATE_OPTIONS, format_func=lambda x: STATE_NAMES.get(x, x))
with col2:
    months_back = st.slider("Months:", 12, 60, 24)
    end_date = datetime.now().strftime('%Y%m%d')
    start_date = (datetime.now() - timedelta(days=30*months_back)).strftime('%Y%m%d')

df = fetch_eia_data(api_key, start_date, end_date, state_id)

if not df.empty:
    # Metrics (latest data)
    latest = df.tail(1)
    col1, col2, col3, col4 = st.columns(4)
    st.metric("Total Sales", f"{latest['SALES'].sum():,.0f} MWh", delta=None)
    st.metric("Avg Price", f"{latest['PRICE'].mean():.3f} $/kWh", delta=None)
    st.metric("Revenue", f"{latest['REVENUE'].sum():,.0f} $M", delta=None)
    st.metric("Customers", f"{latest['CUSTOMERS'].mean():,.0f} M", delta=None)

    # Map (dummy for single state; full map needs all-states fetch)
    st.subheader("Price Trends")
    fig = px.line(df, x='period', y='PRICE', title=f"{STATE_NAMES.get(state_id, state_id)} - Price Over Time")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Full Data")
    st.dataframe(df[['period', 'SALES', 'PRICE', 'REVENUE', 'CUSTOMERS']].round(2))
    
    csv = df.to_csv(index=False).encode()
    st.download_button("Download CSV", csv, "eia_data.csv")
else:
    st.warning("No data. Try 'US' or check API key.")
