import streamlit as st
import ee
import folium
from streamlit_folium import st_folium
from folium.plugins import Draw
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px

# Streamlit Page Setup
st.set_page_config(
    page_title="Land Cover Analysis 🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling - Using the same styling from the previous example
st.markdown("""
    <style>
    /* Base Styling */
    .stApp {
        background: linear-gradient(120deg, #0a192f 0%, #112240 100%);
        color: #e6f1ff;
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

    /* Slider Styling */
    .stSlider > div > label {
        color: #ccd6f6 !important;
        font-weight: 600;
        padding: 0 0 5px 0;
        margin: 0;
        display: block;
    }

    .stSlider > div {
        padding: 10px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        border: 1px solid rgba(100, 255, 218, 0.2);
        transition: all 0.4s ease;
    }

    .stSlider > div:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.3);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }

    .stSlider > div > div {
        background-color: rgba(100, 255, 218, 0.2) !important;
    }

    .stSlider > div > div > div > div {
        background-color: #64ffda !important;
        width: 20px !important;
        height: 20px !important;
        border-radius: 50% !important;
    }
            
    /* Expander Styling */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        color: #e6f1ff !important;
        padding: 10px 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(21, 61, 132, 0.7);
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }
    
    .streamlit-expanderContent {
        background: rgba(21, 61, 132, 0.2);
        border-radius: 0 0 10px 10px;
        padding: 15px;
        border: 1px solid rgba(100, 255, 218, 0.2);
        border-top: none;
    }

    /* Metric Styling */
    .stMetric {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
    
    .stMetric:hover {
        transform: translateY(-7px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }
    
    [data-testid="stMetricLabel"] {
        color: #64ffda !important;
        font-weight: 600;
    }
    
    [data-testid="stMetricValue"] {
        color: #e6f1ff !important;
        font-size: 28px !important;
    }
    
    /* JSON Display */
    .stJson {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 1px solid rgba(100, 255, 218, 0.2);
        color: #e6f1ff !important;
        max-height: 300px;
        overflow-y: auto;
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

# Main Title with animation
st.markdown("""
    <div style="animation: fadeIn 1.2s ease-out;">
        <h1>🌍 Land Cover Analysis </h1>
        <p style="text-align: center; color: #8892b0; margin-top: -15px; margin-bottom: 30px;">
            Analyze forest cover and land use patterns with satellite data
        </p>
    </div>
""", unsafe_allow_html=True)

# Initialize Earth Engine
EE_PROJECT = "ee-coding--api-access"
try:
    ee.Initialize(project=EE_PROJECT)
except Exception as e:
    st.error("Earth Engine authentication failed. Ensure you have API access.")

def get_forest_cover(polygon):  
    """
    Calculate forest & non-forest % along with vegetation type within a polygon.
    Uses ESA WorldCover (2021) for land classification.
    """
    worldcover = ee.Image("ESA/WorldCover/v200/2021").select("Map")

    land_cover_classes = {
        10: "Tree Cover", 20: "Shrubland", 30: "Grassland", 40: "Cropland",
        50: "Built-up", 60: "Bare/Sparse Veg", 70: "Snow/Ice", 80: "Water",
        90: "Wetlands", 95: "Mangroves"
    }

    # Modified parameters to handle larger regions
    area_stats = worldcover.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=polygon,
        scale=100,           # Increased scale from 30m to 100m resolution
        maxPixels=1e9,       # Increased from 1e6 to 1e9
        bestEffort=True      # Added bestEffort parameter
    ).get("Map").getInfo()

    if not area_stats:
        return None  # Handle empty results

    total_pixels = sum(area_stats.values())
    percentages = {land_cover_classes[int(k)]: (v / total_pixels) * 100 
                   for k, v in area_stats.items() if int(k) in land_cover_classes}

    forest_percent = percentages.get("Tree Cover", 0)
    non_forest_percent = 100 - forest_percent

    return {
        "Forest %": forest_percent,
        "Non-Forest %": non_forest_percent,
        "Vegetation Breakdown": percentages
    }
# Function to create a pie chart for land cover
def create_land_cover_chart(percentages):
    # Sort data by percentage (descending)
    sorted_data = sorted(percentages.items(), key=lambda x: x[1], reverse=True)
    labels = [item[0] for item in sorted_data]
    values = [item[1] for item in sorted_data]
    
    # Define colors for different land types
    colors = {
        "Tree Cover": "#2E8B57",      # Forest green
        "Shrubland": "#9ACD32",       # Yellow green
        "Grassland": "#ADFF2F",       # Green yellow
        "Cropland": "#FFD700",        # Gold
        "Built-up": "#708090",        # Slate gray
        "Bare/Sparse Veg": "#DEB887", # Burlywood
        "Snow/Ice": "#F0F8FF",        # Alice blue
        "Water": "#1E90FF",           # Dodger blue
        "Wetlands": "#20B2AA",        # Light sea green
        "Mangroves": "#008080"        # Teal
    }
    
    # Create color map for the chart
    color_map = [colors.get(label, "#64ffda") for label in labels]
    
    # Determine which slices to pull out (explode)
    pull = [0.1 if v > 15 else 0 for v in values]  # Pull out slices > 15%
    
    # Create interactive Plotly pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        textinfo='percent',
        hoverinfo='label+percent',
        hovertemplate='%{label}: %{percent:.1f}%<extra></extra>',
        marker=dict(colors=color_map, line=dict(color='#0a192f', width=2)),
        pull=pull,
        textfont=dict(size=14, color='#e6f1ff', family='Montserrat, sans-serif'),
        insidetextfont=dict(color='#e6f1ff'),
    )])
    
    # Update layout for dark theme
    fig.update_layout(
        title={
            'text': 'Land Cover Distribution',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=20, color='#64ffda', family='Montserrat, sans-serif')
        },
        paper_bgcolor='#0a192f',
        plot_bgcolor='#0a192f',
        legend=dict(
            font=dict(color='#e6f1ff', size=14, family='Montserrat, sans-serif'),
            orientation='h',
            yanchor='bottom',
            y=-0.2,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(10, 25, 47, 0.7)',
            bordercolor='rgba(100, 255, 218, 0.3)'
        ),
        margin=dict(t=80, b=80, l=20, r=20),
        height=500,
    )
    
    # Add hover style
    fig.update_traces(
        hoverlabel=dict(
            bgcolor='#0a192f',
            font_size=14,
            font_family='Montserrat, sans-serif',
            font_color='#e6f1ff',
            bordercolor='#64ffda'
        )
    )
    
    return fig# Streamlit UI - Sidebar Configuration
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>Configuration</h2>", unsafe_allow_html=True)
    
    st.markdown("### Map Settings")
    default_location = st.selectbox(
        "Starting Location",
        options=["Global", "India", "Amazon", "Europe", "Africa"],
        index=1
    )
    
    # Set starting coordinates based on selection
    locations = {
        "Global": [20, 0],
        "India": [20, 78],
        "Amazon": [-3, -60],
        "Europe": [48, 10],
        "Africa": [0, 20]
    }
    
    zoom_level = st.slider("Zoom Level", min_value=2, max_value=10, value=5)
    
    st.markdown("### Analysis Settings")
    show_detailed_breakdown = st.checkbox("Show Detailed Breakdown", value=True)
    include_chart = st.checkbox("Include Pie Chart", value=True)

# Main content
st.markdown("""
<div style="animation: fadeIn 1.5s ease-out;">
    <h2>Interactive Map</h2>
    <p>Draw a polygon on the map to analyze the land cover distribution within that region.</p>
</div>
""", unsafe_allow_html=True)

# Interactive map with selected starting location
m = folium.Map(
    location=locations[default_location], 
    zoom_start=zoom_level, 
    control_scale=True,
    tiles="cartodb positron"  # Using a lighter basemap for better contrast
)
Draw(export=True, position='topleft').add_to(m)
folium.LayerControl().add_to(m)

# Capture drawn polygon
drawn_features = st_folium(m, width="100%", height=500, key="map")

# Check for drawn polygons
if drawn_features and "all_drawings" in drawn_features and drawn_features["all_drawings"]:
    geojson = drawn_features["all_drawings"][0]["geometry"]
    coords = geojson["coordinates"][0]  # Extract first polygon
    polygon = ee.Geometry.Polygon(coords)
    
    with st.expander("📍 Selected Polygon Coordinates", expanded=False):
        st.json(coords)
    
    # Analysis section
    st.markdown("<h2>🌱 Land Cover Analysis Results</h2>", unsafe_allow_html=True)
    
    # Fetch land cover data
    land_cover_data = get_forest_cover(polygon)
    
    if land_cover_data:
        # Display metrics in a row
        col1, col2 = st.columns(2)
        col1.metric("Forest Cover (%)", f"{land_cover_data['Forest %']:.2f}")
        col2.metric("Non-Forest Cover (%)", f"{land_cover_data['Non-Forest %']:.2f}")
        
        # Display detailed breakdown and chart
        # Display detailed breakdown and chart
        if show_detailed_breakdown:
            st.markdown("<h3>Land Cover Composition</h3>", unsafe_allow_html=True)
            
            # Display breakdown table
            df = pd.DataFrame(
                list(land_cover_data["Vegetation Breakdown"].items()), 
                columns=["Land Cover Type", "Percentage"]
            )
            # Sort by percentage (highest first)
            df = df.sort_values("Percentage", ascending=False)
            # Format percentage to 2 decimal places
            df["Percentage"] = df["Percentage"].apply(lambda x: f"{x:.2f}%")
            st.dataframe(df, use_container_width=True)
            
            # Display pie chart below the table if enabled
            if include_chart:
                st.markdown("<h3>Land Cover Distribution</h3>", unsafe_allow_html=True)
                fig = create_land_cover_chart(land_cover_data["Vegetation Breakdown"])
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No land cover data found for the selected region. Try selecting a larger area.")

# Footer
st.markdown("""
<footer>
    <p>Created with ❤️ using Streamlit and Google Earth Engine | 
    <a href="https://github.com/username/land-cover-analysis" target="_blank">GitHub</a>
    </p>
</footer>
""", unsafe_allow_html=True)