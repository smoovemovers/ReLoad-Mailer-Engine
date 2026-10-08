import streamlit as st
import pandas as pd
import json
import os
import datetime

# Page Configuration
st.set_page_config(
    page_title="ReloLead Engine | Daily Verified Leads",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 ReloLead Engine | Verified Residential Mailers")
st.caption("Auto-Updating Daily Pipeline | 30.0-Mile Radius of Beaverton, OR (97005)")

# Sidebar Controls
st.sidebar.header("🎛️ Lead Filters")
price_range = st.sidebar.slider("Price Range ($)", 300000, 2000000, (500000, 1200000), step=25000)
min_price, max_price = price_range

target_statuses = st.sidebar.multiselect(
    "Listing Statuses",
    ["Pending", "Under Contract", "Active (DOM < 14)"],
    default=["Pending", "Under Contract", "Active (DOM < 14)"]
)

# Load JSON Data
@st.cache_data(ttl=3600)
def load_daily_data():
    if os.path.exists("daily_leads.json"):
        with open("daily_leads.json", "r") as f:
            data = json.load(f)
            df = pd.DataFrame(data["leads"])
            last_updated = data.get("last_updated", "Today")
            return df, last_updated
    else:
        st.error("daily_leads.json file not found. Run scraper.py first.")
        return pd.DataFrame(), "N/A"

df_leads, last_updated = load_daily_data()

if not df_leads.empty:
    df_filtered = df_leads[
        (df_leads['price'] >= min_price) & 
        (df_leads['price'] <= max_price) & 
        (df_leads['status'].isin(target_statuses))
    ]

    # Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Verified Homes Available", f"{len(df_filtered)}")
    col2.metric("Avg Listing Price", f"${df_filtered['price'].mean():,.0f}" if not df_filtered.empty else "$0")
    col3.metric("Last Pipeline Sync", last_updated[:10] if len(last_updated) >= 10 else last_updated)
    col4.metric("City Sort Order", "Alphabetical (A-Z)")

    st.markdown("---")

    # Table Display
    st.subheader("📋 Verified Direct Mail Destinations (Sorted Alphabetically by City)")
    st.dataframe(
        df_filtered[[
            "full_address", "city", "zip", "type", "price", 
            "status", "distance_miles"
        ]],
        column_config={
            "full_address": "Complete USPS Delivery Address",
            "city": "City",
            "zip": "ZIP Code",
            "type": "Property Type",
            "price": st.column_config.NumberColumn("Price ($)", format="$%d"),
            "status": "Listing Status",
            "distance_miles": st.column_config.NumberColumn("Distance (mi)", format="%.2f mi")
        },
        use_container_width=True,
        hide_index=True
    )

    # Download CSV Action
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"📥 Download Today's Direct Mail CSV ({len(df_filtered)} Verified Addresses)",
        data=csv_data,
        file_name=f"Verified_ReloLeads_{datetime.date.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        type="primary"
    )
