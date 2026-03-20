import streamlit as st
import pandas as pd
import requests
from datetime import datetime

st.set_page_config(layout="wide", page_title="EIA Electricity Dashboard")

# --- UI Setup ---
st.title("⚡ EIA Electricity Summary Stats")

# Summary Text Box
st.info("""
**Dashboard Summary:**  
This tool provides a real-time overview of U.S. residential, commercial, and industrial electricity statistics, including total sales, average prices, and customer counts. 

**Data Source:**  
All data is pulled directly from the **U.S. Energy Information Administration (EIA) Open Data API**. You can find the raw datasets, documentation, and additional energy insights at the [EIA Official Website](https://www.eia.gov/opendata/).
""")

# Sidebar for Filters
st.sidebar.header("Filter Data")

# State selection (including US as a total)
states = ["US", "AK", "AL", "AR", "AZ", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "IA", "ID", "IL", "IN", "KS", "KY", "LA", "MA", "MD", "ME", "MI", "MN", "MO", "MS", "MT", "NC", "ND", "NE", "NH", "NJ", "NM", "NV", "NY", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VA", "VT", "WA", "WI", "WV", "WY"]
selected_state = st.sidebar.selectbox("Select Area", states, index=0)

# Date Range selection
# EIA monthly data usually lags by 2-3 months, so we set a safe default range
col_start, col_end = st.sidebar.columns(2)
start_date = col_start.date_input("Start Date", value=datetime(2023, 1, 1))
end_date = col_end.date_input("End Date", value=datetime.now())

# Sector selection (Optional but helpful)
sector = st.sidebar.selectbox("Sector", ["Residential (RES)", "Commercial (COM)", "Industrial (IND)"], index=0)
sector_id = sector.split("(")[1].replace(")", "")

api_key = st.secrets.get("EIA_API_KEY")

@st.cache_data(ttl=1800)
def fetch_data(state, sector, start, end):
    # Format dates to YYYY-MM as required by EIA API
    formatted_start = start.strftime("%Y-%m")
    formatted_end = end.strftime("%Y-%m")
    
    url = "https://api.eia.gov/v2/electricity/retail-sales/data"
    params = {
        'api_key': api_key,
        'data[]': ['revenue', 'sales', 'price', 'customers'],
        'facets[sectorid][]': sector,
        'facets[stateid][]': state,
        'frequency': 'monthly',
        'start': formatted_start,
        'end': formatted_end,
        'sort[0][column]': 'period',
        'sort[0][direction]': 'desc'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status() # Raise error for bad status codes
        
        json_data = response.json()
        data = json_data.get('response', {}).get('data', [])
        
        if not data:
            return pd.DataFrame(), "No data found for this specific selection/date range."
            
        df = pd.DataFrame(data)
        df['period'] = pd.to_datetime(df['period'])
        
        # Clean numeric columns
        for col in ['revenue', 'sales', 'price', 'customers']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return df.sort_values('period'), None

    except requests.exceptions.RequestException as e:
        return pd.DataFrame(), f"Connection Error: {str(e)}"
    except Exception as e:
        return pd.DataFrame(), f"System Error: {str(e)}"

# --- Main Logic ---
if not api_key:
    st.error("❌ Add EIA_API_KEY to your Streamlit secrets.")
elif start_date > end_date:
    st.warning("⚠️ Start date must be before end date.")
else:
    with st.spinner(f"Fetching data for {selected_state}..."):
        df, error_msg = fetch_data(selected_state, sector_id, start_date, end_date)

    if error_msg:
        st.error(f"❌ {error_msg}")
    elif not df.empty:
        # Success Layout
        st.markdown(f"### {selected_state} - {sector.split(' ')[0]} Electricity Data")
        
        # Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Sales (MWh)", f"{df['sales'].sum():,.0f}")
        m2.metric("Avg Price (¢/kWh)", f"{df['price'].mean():.2f}")
        m3.metric("Total Rev ($M)", f"{df['revenue'].sum():,.0f}")
        m4.metric("Avg Customers", f"{df['customers'].mean():,.0f}")

        # Charts
        tab1, tab2 = st.tabs(["📈 Price Trend", "📊 Sales Volume"])
        with tab1:
            st.line_chart(df.set_index('period')['price'])
        with tab2:
            st.bar_chart(df.set_index('period')['sales'])

        # Data Preview
        with st.expander("View Raw Data"):
            st.dataframe(df.round(3), use_container_width=True)
            st.download_button("📥 Download CSV", df.to_csv(index=False).encode(), "eia_export.csv")
    else:
        st.info("The API returned an empty dataset. Try expanding your date range or checking if the area has reported data for these months.")
