import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

st.set_page_config(layout="wide", page_title="EIA Electricity Comparison")

st.title("⚡ EIA Electricity Comparison Dashboard")

# Summary Text Box
st.info("""
**Dashboard Summary:**  
This tool provides a real-time overview of U.S. residential, commercial, and industrial electricity statistics, including total sales, average prices, and customer counts. 

**Data Source:**  
All data is pulled directly from the **U.S. Energy Information Administration (EIA) Open Data API**. You can find the raw datasets, documentation, and additional energy insights at the [EIA Official Website](https://www.eia.gov/opendata/).
""")

# --- Sidebar ---
st.sidebar.header("Filter Data")
states_list = ["US", "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
selected_states = st.sidebar.multiselect("Select Areas to Compare", states_list, default=["CA", "TX"])

col_start, col_end = st.sidebar.columns(2)
start_date = col_start.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = col_end.date_input("End Date", value=datetime.now())

sector_label = st.sidebar.selectbox("Sector", ["Residential (RES)", "Commercial (COM)", "Industrial (IND)"], index=0)
sector_id = sector_label.split("(")[1].replace(")", "").strip()

api_key = st.secrets.get("EIA_API_KEY")

@st.cache_data(ttl=1800)
def fetch_comparison_data(states, sector, start, end, api_key):
    if not states:
        return pd.DataFrame()

    url = "https://api.eia.gov/v2/electricity/retail-sales/data/"
    length = 5000
    params = {
        'api_key': api_key,
        'data[]': ['revenue', 'sales', 'price', 'customers'],
        'facets[sectorid][]': [sector],
        'facets[stateid][]': list(states),
        'frequency': 'monthly',
        'start': start.strftime("%Y-%m"),
        'end': end.strftime("%Y-%m"),
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc',
        'length': length,
        'offset': 0
    }

    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    try:
        all_data = []
        offset = 0

        while True:
            params['offset'] = offset
            response = session.get(url, params=params, timeout=(5, 30))
            response.raise_for_status()
            resp_json = response.json().get('response', {})
            batch = resp_json.get('data', [])
            total = int(resp_json.get('total', 0))
            all_data.extend(batch)

            offset += length
            if offset >= total or not batch:
                break

        if not all_data: 
            return pd.DataFrame()

        df = pd.DataFrame(all_data)
        df['period'] = pd.to_datetime(df['period'])
        
        # Ensure columns exist and convert to numeric
        cols_to_fix = ['revenue', 'sales', 'price', 'customers']
        for col in cols_to_fix:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df

    except Exception as e:
        st.error(f"API Error: {e}")
        return pd.DataFrame()

# --- Main Logic ---
if not api_key:
    st.error("❌ Add EIA_API_KEY to secrets.")
elif not selected_states:
    st.warning("⚠️ Please select at least one state.")
else:
    with st.spinner("Fetching comparison data..."):
        # Convert selected_states to tuple for hashing/caching
        df = fetch_comparison_data(tuple(selected_states), sector_id, start_date, end_date, api_key)

    if not df.empty:
        # --- Metrics ---
        st.subheader(f"Comparison Summary ({sector_label})")
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg Price", f"{df['price'].mean():.2f} ¢/kWh")
        m2.metric("Total Sales", f"{df['sales'].sum():,.0f} MWh")
        m3.metric("Total Customers", f"{df['customers'].sum():,.0f}")

        # --- Comparison Charts ---
        tab1, tab2 = st.tabs(["📈 Price Trend", "📊 Sales Volume"])

        with tab1:
            # Pivot table to make plotting easier
            price_chart_data = df.pivot_table(index='period', columns='stateid', values='price')
            st.line_chart(price_chart_data)

        with tab2:
            sales_chart_data = df.pivot_table(index='period', columns='stateid', values='sales')
            st.bar_chart(sales_chart_data)

        with st.expander("View Raw Combined Data"):
            st.dataframe(df.sort_values(['period', 'stateid']), use_container_width=True)
    else:
        st.info("No data returned. Try adjusting your date range or selecting different states.")
