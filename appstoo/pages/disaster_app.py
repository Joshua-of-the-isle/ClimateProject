import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from gdacs.api import GDACSAPIReader

# Streamlit Page Setup
st.set_page_config(
    page_title="Global Disaster Tracker 🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling
st.markdown("""
    <style>
    /* Base Styling */
    .stApp {
        background: linear-gradient(120deg, #0a192f 0%, #112240 100%);
        color:#e6f1ff;
        font-family: 'Montserrat', sans-serif;
    }
            /* Navbar Styling */
    .stApp > header {
        background: linear-gradient(120deg, #0a192f 0%, #112240 100%);
        color: #e6f1ff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }

    .stToolbar {
        background: rgba(21, 61, 132, 0.4);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(100, 255, 218, 0.2);
    }

    /* Sidebar Styling */
    .sidebar .sidebar-content {
        background: rgba(21, 61, 132, 0.4);
        backdrop-filter: blur(10px);
        border-radius: 0 20px 20px 0;
        padding: 25px;
        box-shadow: 5px 0 15px rgba(0,0,0,0.4);
    }
    
    .sidebar .stSelectbox > div > div {
        background: #64ffda;
        color: #0a192f;
        font-weight: 600;
        border-radius: 12px;
        padding: 12px;
        transition: all 0.4s ease;
    }
    
    .sidebar .stSelectbox > div > div:hover {
        background: #00eeff;
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.3);
    }
    
    /* Apply the same style to number input */
    .sidebar .stNumberInput > div > div {
        background: #64ffda;
        color: #0a192f;
        font-weight: 600;
        border-radius: 12px;
        padding: 12px;
        transition: all 0.4s ease;
    }
    
    .sidebar .stNumberInput > div > div:hover {
        background: #00eeff;
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.3);
    }

    /* Title Styling */
    h1 {
        color: #64ffda;
        text-align: center;
        padding: 30px 0;
        font-weight: 800;
        text-shadow: 0 3px 5px rgba(0,0,0,0.3);
        background: linear-gradient(90deg, #64ffda, #00eeff, #8892b0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientText 3s ease infinite;
        background-size: 200% 200%;
    }

    /* Subheader Styling */
    h2 {
        color: #ccd6f6;
        border-bottom: 3px solid #64ffda;
        padding-bottom: 8px;
        margin: 25px 0 15px 0;
        display: inline-block;
    }

    /* Dataframe Styling */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
    
    .stDataFrame:hover {
        transform: translateY(-7px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }

    /* Warning Styling */
    .stAlert {
        background: rgba(21, 61, 132, 0.7);
        color: #e6f1ff;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        border-left: 5px solid #64ffda;
        transition: all 0.4s ease;
    }
    
    .stAlert:hover {
        background: rgba(30, 75, 155, 0.7);
        transform: scale(1.03);
    }

    /* Map Container */
    .folium-map {
        border-radius: 15px;
        background: rgba(255, 255, 255, 0.05);
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(100, 255, 218, 0.2);
        margin-top: 20px;
    }

    /* Footer */
    footer {
        text-align: center;
        padding: 30px 0;
        color: #8892b0;
        font-size: 16px;
        border-top: 1px solid rgba(100, 255, 218, 0.2);
        margin-top: 40px;
    }
    
    footer a {
        color: #64ffda;
        text-decoration: none;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    
    footer a:hover {
        color: #00eeff;
        text-decoration: underline;
    }

    /* Markdown Text */
    .stMarkdown {
        color: #8892b0;
        line-height: 1.7;
    }

    /* Animation */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes gradientText {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Button Styling */
    .stButton button {
        background: #64ffda;
        color: #0a192f;
        border-radius: 12px;
        font-weight: 600;
        border: none;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background: #00eeff;
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }

    /* Disaster Alert Level Indicators */
    .disaster-alert {
        display: inline-block;
        width: 15px;
        height: 15px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .alert-red {
        background-color: #ff5a5f;
        box-shadow: 0 0 10px #ff5a5f;
    }
    
    .alert-orange {
        background-color: #ffbd59;
        box-shadow: 0 0 10px #ffbd59;
    }
    
    .alert-green {
        background-color: #3ec78f;
        box-shadow: 0 0 10px #3ec78f;
    }

    /* Sidebar Header */
    .sidebar-header {
        background: rgba(100, 255, 218, 0.1);
        padding: 15px;
        border-radius: 12px;
        margin-bottom: 20px;
        border-left: 3px solid #64ffda;
    }

    /* Responsive Design */
    @media (max-width: 768px) {
        h1 { font-size: 32px; }
        h2 { font-size: 24px; }
        .sidebar .sidebar-content { padding: 15px; }
    }
    </style>
""", unsafe_allow_html=True)

# Add custom fonts
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Initialize the GDACS API client
client = GDACSAPIReader()

def get_recent_disasters_df(event_type: str = None, limit: int = 20):
    print(f"Event type: {event_type}, Limit: {limit}")
    if event_type is None:
        geojson_data = client.latest_events(limit=limit)
    else:
        geojson_data = client.latest_events(limit=limit, event_type=event_type)

    geojson_dict = dict(geojson_data)
    features = geojson_dict.get("features", [])

    event_records = []
    for feature in features:
        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [None, None])

        event_records.append({
            "Event Type": properties.get("eventtype"),
            "Event ID": properties.get("eventid"),
            "Country": properties.get("country"),
            "Latitude": coordinates[1],  
            "Longitude": coordinates[0],
            "Alert Level": properties.get("alertlevel"),
            "Alert Score": properties.get("alertscore"),
            "Event Name": properties.get("name") or "Unknown",
            "Description": properties.get("description"),
            "From Date": properties.get("fromdate"),
            "To Date": properties.get("todate"),
            "Severity": properties.get("severitydata", {}).get("severity"),
            "Severity Text": properties.get("severitydata", {}).get("severitytext"),
            "Report URL": properties.get("url", {}).get("report")
        })

    df = pd.DataFrame(event_records)
    return df

# Sidebar: Event Type Selection with enhanced styling
st.sidebar.markdown('<div class="sidebar-header"><h3>🔍 Filter Disasters</h3></div>', unsafe_allow_html=True)
event_types = ["All", "Earthquake EQ", "Flood FL", "Cyclone TC", "Volcanic VO", "Wildfire WF", "Drought DR"]
selected_type = st.sidebar.selectbox("Select Event Type", event_types)

# Add event limit selection to sidebar
st.sidebar.markdown('<div class="sidebar-header"><h3>🔢 Event Display</h3></div>', unsafe_allow_html=True)
event_limit = st.sidebar.number_input(
    "Number of events to display",
    min_value=5,
    max_value=50,
    value=20,
    step=5,
    help="Choose how many events you want to display (5-50)"
)

# Add legend to sidebar
st.sidebar.markdown('<div class="sidebar-header"><h3>🚨 Alert Level Legend</h3></div>', unsafe_allow_html=True)
st.sidebar.markdown('<span class="disaster-alert alert-red"></span> Red - Severe Impact', unsafe_allow_html=True)
st.sidebar.markdown('<span class="disaster-alert alert-orange"></span> Orange - Moderate Impact', unsafe_allow_html=True)
st.sidebar.markdown('<span class="disaster-alert alert-green"></span> Green - Minor Impact', unsafe_allow_html=True)

# Fetch Data with the user-specified limit
if selected_type == "All":
    df = get_recent_disasters_df(limit=event_limit)
else:
    df = get_recent_disasters_df(event_type=selected_type.split(" ")[1], limit=event_limit)

# Main Title with animation
st.markdown("""
    <div style="animation: fadeIn 1.2s ease-out;">
        <h1>🌍 Global Disaster Tracker</h1>
        <p style="text-align: center; color: #8892b0; margin-top: -15px; margin-bottom: 30px;">
            Real-time monitoring of global disasters powered by GDACS data
        </p>
    </div>
""", unsafe_allow_html=True)

# Dashboard Overview
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; text-align: center; height: 150px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(100, 255, 218, 0.2);">
            <h3 style="color: #64ffda; margin-bottom: 10px;">Total Events</h3>
            <p style="font-size: 32px; font-weight: bold; color: #e6f1ff;">{}</p>
        </div>
    """.format(len(df)), unsafe_allow_html=True)

with col2:
    alert_counts = df["Alert Level"].value_counts()
    red_count = alert_counts.get("Red", 0)
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; text-align: center; height: 150px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(100, 255, 218, 0.2);">
            <h3 style="color: #ff5a5f; margin-bottom: 10px;">Red Alerts</h3>
            <p style="font-size: 32px; font-weight: bold; color: #e6f1ff;">{}</p>
        </div>
    """.format(red_count), unsafe_allow_html=True)

with col3:
    event_type_counts = df["Event Type"].value_counts()
    most_common_type = event_type_counts.idxmax() if not event_type_counts.empty else "None"
    st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; text-align: center; height: 150px; display: flex; flex-direction: column; justify-content: center; border: 1px solid rgba(100, 255, 218, 0.2);">
            <h3 style="color: #00eeff; margin-bottom: 10px;">Most Common Event</h3>
            <p style="font-size: 24px; font-weight: bold; color: #e6f1ff;">{}</p>
        </div>
    """.format(most_common_type), unsafe_allow_html=True)

# Show Data Table
st.subheader(f"📊 Recent Disasters (Showing {len(df)} events)")
st.dataframe(df, height=400)

# Map Visualization with Folium
st.subheader("🗺️ Disaster Locations")
if not df.empty:
    center_lat = df["Latitude"].mean()
    center_lon = df["Longitude"].mean()
    
    m = folium.Map(
        location=[center_lat, center_lon], 
        zoom_start=2, 
        tiles="CartoDB dark_matter"  # Dark theme map
    )

    marker_cluster = MarkerCluster().add_to(m)

    alert_colors = {
        "Green": "#3ec78f",
        "Orange": "#ffbd59",
        "Red": "#ff5a5f"
    }

    for _, row in df.iterrows():
        popup_content = f"""
        <div style="font-family: 'Montserrat', sans-serif; min-width: 200px;">
            <h4 style="color: #0a192f; margin-bottom: 10px; border-bottom: 2px solid #64ffda; padding-bottom: 5px;">
                {row['Event Name']}
            </h4>
            <b style="color: #0a192f;">Country:</b> {row['Country']}<br>
            <b style="color: #0a192f;">Severity:</b> {row['Severity']} - {row['Severity Text']}<br>
            <b style="color: #0a192f;">Alert Level:</b> {row['Alert Level']}<br>
            <b style="color: #0a192f;">From:</b> {row['From Date']}<br>
            <b style="color: #0a192f;">To:</b> {row['To Date']}<br>
            <a href="{row['Report URL']}" target="_blank" style="display: inline-block; margin-top: 10px; background: #64ffda; color: #0a192f; padding: 5px 10px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                📄 View Full Report
            </a>
        </div>
        """
        
        color = alert_colors.get(row["Alert Level"], "#64ffda")

        folium.CircleMarker(
            location=[row["Latitude"], row["Longitude"]],
            radius=12,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.7,
            popup=folium.Popup(popup_content, max_width=300)
        ).add_to(marker_cluster)

    folium_static(m)
else:
    st.warning("No disaster events available for the selected type.")

# Footer with enhanced styling
st.markdown("""
    <footer>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
            <p>🌎 Powered by <a href="https://www.gdacs.org" target="_blank">GDACS</a> | Built with ❤️ using Streamlit</p>
            <p style="font-size: 14px; color: #64ffda;">Stay informed, stay prepared, stay safe.</p>
        </div>
    </footer>
""", unsafe_allow_html=True)
