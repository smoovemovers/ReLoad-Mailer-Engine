import streamlit as st
import pandas as pd
import datetime

# Page Configuration
st.set_page_config(
    page_title="ReloLead Engine | Daily Moving Leads",
    page_icon="🚚",
    layout="wide"
)

# Header
st.title("🚚 ReloLead Engine")
st.caption("Automated High-Value Moving Lead Pipeline | 30-Mile Radius of 97005 (Beaverton, OR)")

# Sidebar Filters
st.sidebar.header("🎛️ Lead Filters")
price_range = st.sidebar.slider("Price Range ($)", 300000, 2000000, (500000, 1200000), step=25000)
min_price, max_price = price_range

target_statuses = st.sidebar.multiselect(
    "Target Listing Statuses",
    ["Pending", "Under Contract", "Active (DOM < 14)"],
    default=["Pending", "Under Contract"]
)

# Sample Daily Data Pipeline
@st.cache_data(ttl=21600)
def load_daily_leads():
    raw_data = [
        {"ID": "RLE-201", "Address": "1830 A Ave", "City": "Lake Oswego", "ZIP": "97034", "Price": 1150000, "Status": "Under Contract", "Est. Move Window": "Oct 20 – Nov 05", "Score": 98},
        {"ID": "RLE-202", "Address": "14205 SW Beard Rd", "City": "Beaverton", "ZIP": "97008", "Price": 549000, "Status": "Pending", "Est. Move Window": "Oct 15 – Oct 29", "Score": 97},
        {"ID": "RLE-203", "Address": "2240 Sherwood Blvd", "City": "Sherwood", "ZIP": "97140", "Price": 610000, "Status": "Pending", "Est. Move Window": "Oct 18 – Nov 02", "Score": 97},
        {"ID": "RLE-204", "Address": "2100 SW River Pkwy #802", "City": "Portland", "ZIP": "97201", "Price": 675000, "Status": "Under Contract", "Est. Move Window": "Oct 25 – Nov 10", "Score": 96},
        {"ID": "RLE-205", "Address": "12840 SW Crestview Dr", "City": "Beaverton", "ZIP": "97008", "Price": 725000, "Status": "Pending", "Est. Move Window": "Oct 14 – Oct 28", "Score": 98},
        {"ID": "RLE-206", "Address": "15420 SW Bull Mountain Rd", "City": "Tigard", "ZIP": "97224", "Price": 895000, "Status": "Under Contract", "Est. Move Window": "Oct 22 – Nov 08", "Score": 97},
        {"ID": "RLE-207", "Address": "1140 SW Timberline Dr", "City": "Lake Oswego", "ZIP": "97034", "Price": 1195000, "Status": "Pending", "Est. Move Window": "Oct 12 – Oct 26", "Score": 98},
        {"ID": "RLE-208", "Address": "2210 Willamette Falls Dr", "City": "West Linn", "ZIP": "97068", "Price": 780000, "Status": "Under Contract", "Est. Move Window": "Oct 28 – Nov 12", "Score": 96},
        {"ID": "RLE-209", "Address": "8950 SW Laurel St", "City": "Beaverton", "ZIP": "97005", "Price": 615000, "Status": "Pending", "Est. Move Window": "Oct 16 – Oct 30", "Score": 98},
        {"ID": "RLE-210", "Address": "17850 SW Farmington Rd", "City": "Aloha", "ZIP": "97007", "Price": 535000, "Status": "Pending", "Est. Move Window": "Oct 19 – Nov 03", "Score": 95},
    ]
    return pd.DataFrame(raw_data)

today = datetime.date.today()
st.subheader(f"📅 Daily Active Leads — {today.strftime('%A, %B %d, %Y')}")

df_leads = load_daily_leads()
df_filtered = df_leads[
    (df_leads['Price'] >= min_price) & 
    (df_leads['Price'] <= max_price) & 
    (df_leads['Status'].isin(target_statuses))
]

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Qualified Leads", f"{len(df_filtered)}")
col2.metric("Avg Listing Price", f"${df_filtered['Price'].mean():,.0f}" if not df_filtered.empty else "$0")
col3.metric("Under Contract / Pending", f"{len(df_filtered[df_filtered['Status'].isin(['Pending', 'Under Contract'])])}")
col4.metric("Schedule", "Mon–Sat 6:00 AM PST")

st.markdown("---")

# Data Table
st.dataframe(
    df_filtered,
    column_config={"Price": st.column_config.NumberColumn("Price ($)", format="$%d")},
    use_container_width=True,
    hide_index=True
)

# Download CSV Action
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Today's Direct Mail CSV",
    data=csv_data,
    file_name=f"ReloLead_Batch_{today.strftime('%Y%m%d')}.csv",
    mime="text/csv",
    type="primary"
)
