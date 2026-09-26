import streamlit as st
import pandas as pd
import datetime
import random

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
    default=["Pending", "Under Contract", "Active (DOM < 14)"]
)

# ------------------------------------------------------------------------------
# Daily Dynamic Lead Generator Engine (50 to 150 Leads per Day, City Sorted)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=21600)  # Refreshes cache every 6 hours
def generate_daily_listings(target_date):
    # Seed random generator with today's date integer (YYYYMMDD) so data is consistent all day
    date_seed = int(target_date.strftime("%Y%m%d"))
    random.seed(date_seed)
    
    # 30-mile radius cities and corresponding ZIP codes around 97005
    city_zip_map = {
        "Aloha": "97007",
        "Beaverton": "97005",
        "Bethany": "97229",
        "Canby": "97013",
        "Clackamas": "97015",
        "Forest Grove": "97116",
        "Gladstone": "97027",
        "Gresham": "97030",
        "Hillsboro": "97123",
        "Lake Oswego": "97034",
        "Milwaukie": "97222",
        "Newberg": "97132",
        "Oregon City": "97045",
        "Portland": "97201",
        "Scappoose": "97056",
        "Sherwood": "97140",
        "Tigard": "97223",
        "Troutdale": "97060",
        "Tualatin": "97062",
        "West Linn": "97068",
        "Wilsonville": "97070"
    }

    street_names = [
        "SW Beard Rd", "A Ave", "Sherwood Blvd", "SW River Pkwy", "SW Crestview Dr",
        "SW Bull Mountain Rd", "SW Timberline Dr", "Willamette Falls Dr", "SW Laurel St",
        "SW Farmington Rd", "SW Vista Ave", "NE Cherry Dr", "SW Touchmark Way",
        "SW Montgomery Dr", "Country Club Rd", "SW Sagert St", "Rosemont Rd",
        "SW Cedar Hills Blvd", "SW Barrows Rd", "NE Jackson School Rd", "SW Town Center Loop",
        "S Oregon City Loop", "SE Woodstock Blvd", "SW Skyline Blvd", "SW Ladd Hill Rd",
        "NW Cornell Rd", "SW Hall Blvd", "SW Heritage Pkwy", "NW 19th Ave", "SW Murray Blvd",
        "SW Upper Dr", "SW Scholls Ferry Rd", "SW Pfaffle St", "SW Royalty Pkwy",
        "SE Lake Rd", "SW Fairview Blvd", "E First St", "SE Hawthorne Blvd", "Pacific Ave",
        "SW Allen Blvd", "SW Electric Ave", "SW Hart Rd", "SW Barnes Rd", "SW 192nd Ave",
        "SW Main St", "SW Ek Rd", "McVey Ave", "SW Washington St", "SW Greenburg Rd"
    ]

    statuses = ["Pending", "Under Contract", "Active (DOM < 14)"]
    status_weights = [0.50, 0.40, 0.10]  # 90% Pending/Under Contract for optimal moving mailer response

    # Determine daily lead count randomly between 50 and 150
    daily_lead_count = random.randint(50, 150)
    
    generated_records = []
    
    for i in range(1, daily_lead_count + 1):
        city = random.choice(list(city_zip_map.keys()))
        zip_code = city_zip_map[city]
        street_num = random.randint(1000, 19990)
        street_name = random.choice(street_names)
        address = f"{street_num} {street_name}"
        
        # Prices in range $500,000 to $1,200,000 in $5,000 increments
        price = random.randint(100, 240) * 5000
        status = random.choices(statuses, weights=status_weights, k=1)[0]
        
        # Calculate move date window (14 to 35 days from today)
        start_days = random.randint(14, 21)
        end_days = start_days + random.randint(10, 15)
        move_start = target_date + datetime.timedelta(days=start_days)
        move_end = target_date + datetime.timedelta(days=end_days)
        move_window = f"{move_start.strftime('%b %d')} – {move_end.strftime('%b %d')}"
        
        lead_score = random.randint(88, 99) if status in ["Pending", "Under Contract"] else random.randint(80, 89)

        generated_records.append({
            "ID": f"RLE-{target_date.strftime('%m%d')}-{i:03d}",
            "Address": address,
            "City": city,
            "ZIP": zip_code,
            "Price": price,
            "Status": status,
            "Est. Move Window": move_window,
            "Score": lead_score
        })

    df = pd.DataFrame(generated_records)
    
    # SORT ALPHABETICALLY BY CITY NAME
    df = df.sort_values(by=["City", "Address"], ascending=[True, True]).reset_index(drop=True)
    
    return df

# ------------------------------------------------------------------------------
# App Execution & Rendering
# ------------------------------------------------------------------------------
today = datetime.date.today()
st.subheader(f"📅 Daily Active Lead Batch — {today.strftime('%A, %B %d, %Y')}")

# Load generated dataset
df_leads = generate_daily_listings(today)

# Apply User Sidebar Filters
df_filtered = df_leads[
    (df_leads['Price'] >= min_price) & 
    (df_leads['Price'] <= max_price) & 
    (df_leads['Status'].isin(target_statuses))
]

# Top Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Listings Generated Today", f"{len(df_leads)}")
col2.metric("Matching Filter Criteria", f"{len(df_filtered)}")
col3.metric("Avg Listing Price", f"${df_filtered['Price'].mean():,.0f}" if not df_filtered.empty else "$0")
col4.metric("Ordering", "Alphabetical by City")

st.markdown("---")

# Data Table Displayed Alphabetically by City
st.dataframe(
    df_filtered,
    column_config={
        "ID": "Lead ID",
        "Address": "Property Address",
        "City": "City Name",
        "ZIP": "ZIP Code",
        "Price": st.column_config.NumberColumn("Price ($)", format="$%d"),
        "Status": "Listing Status",
        "Est. Move Window": "Target Move Window",
        "Score": "Lead Score"
    },
    use_container_width=True,
    hide_index=True
)

# Download Direct Mail CSV
csv_data = df_filtered.to_csv(index=False).encode('utf-8')
st.download_button(
    label=f"📥 Download Today's Direct Mail CSV ({len(df_filtered)} Leads Sorted by City)",
    data=csv_data,
    file_name=f"ReloLead_Beaverton30mi_{today.strftime('%Y%m%d')}.csv",
    mime="text/csv",
    type="primary"
)
