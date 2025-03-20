import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import Draw
import json
import os
import xarray as xr
import numpy as np
import geopandas as gpd
import rasterio.features
from shapely.geometry import shape, box
import matplotlib.pyplot as plt
import calendar
import matplotlib.patheffects as PathEffects


# Streamlit Page Setup
st.set_page_config(
    page_title="Monthly Temperature Change Calculator 🌡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Styling - Using the same styling from the first example
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
    background-color: rgba(100, 255, 218, 0.2) !important; /* Track background */
}

/* Inner green box (thumb) - Make it larger */
.stSlider > div > div > div > div {
    background-color: #64ffda !important;
    width: 20px !important; /* Increase width (default is usually smaller, e.g., 10-15px) */
    height: 20px !important; /* Increase height (default is usually smaller) */
    border-radius: 50% !important; /* Optional: Keeps it circular */
}
            
    /* File Uploader Styling */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
    }
    
    .stFileUploader > div:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }
    
    /* GeoJSON Upload Section Text - Making it white */
    .stFileUploader label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    .stFileUploader div.uploadedFile {
        color: #ffffff !important;
    }
    
    /* Make all text in the upload section white */
    .stFileUploader p {
        color: #ffffff !important;
    }
    
    /* Upload section header white */
    #-upload-region-data h2 {
        color: #ffffff;
    }
    
    /* Upload instructions white */
    #-upload-region-data p {
        color: #ffffff !important;
    }

    /* Table Styling */
    .stTable {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
        color: #ffffff !important;
    }
    .stTable th, .stTable td {
        color: #ffffff !important; /* Force white text for table headers and cells */
    }
    
    .stTable:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }
    
    /* Chart Container */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
        margin-bottom: 30px;
    }
    
    .chart-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
    }

    /* Temperature Display Boxes */
    .temp-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        transition: all 0.4s ease;
        border: 1px solid rgba(100, 255, 218, 0.2);
        margin-bottom: 20px;
    }
    
    .temp-box:hover {
        transform: translateY(-7px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.4);
        border: 1px solid rgba(100, 255, 218, 0.4);
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
        <h1>🌡️ Monthly Temperature Change Calculator</h1>
        <p style="text-align: center; color: #8892b0; margin-top: -15px; margin-bottom: 30px;">
            Analyze temperature changes by region and time period
        </p>
    </div>
""", unsafe_allow_html=True)

# Function to convert month number to name
def get_month_name(month_num):
    return calendar.month_name[month_num]

# Define the extract_temperature_change function
def extract_temperature_change(netcdf_path, polygon, year1, year2, warming_degree=1):
    """
    Extracts monthly temperature changes between two years for a given polygon.
    
    :param netcdf_path: Path to the NetCDF file.
    :param polygon: A shapely polygon defining the region of interest.
    :param year1: First year for comparison.
    :param year2: Second year for comparison.
    :param warming_degree: The degree of warming to apply beyond natural warming. Default is 1.
    :return: Dictionary with monthly temperatures for both years and the change.
    """
    # Load the dataset
    ds = xr.open_dataset(netcdf_path)
    
    # Debug info in a styled container
    with st.expander("Debug Information", expanded=False):
        st.markdown("<h3 style='color: #64ffda;'>Dataset Information</h3>", unsafe_allow_html=True)
        st.write("Available variables in NetCDF:", list(ds.variables))
        lats, lons = ds.lat.values, ds.lon.values
        data_bounds = box(lons.min(), lats.min(), lons.max(), lats.max())
        st.write("NetCDF Data Bounds (lon_min, lat_min, lon_max, lat_max):", data_bounds.bounds)
        st.write("Polygon Bounds (lon_min, lat_min, lon_max, lat_max):", polygon.bounds)
    
    # Check spatial overlap
    if not data_bounds.intersects(polygon):
        st.warning("The drawn polygon does not intersect with the NetCDF data extent. Please adjust the polygon.")
        return None
    
    # Convert polygon to a mask
    mask = np.zeros((len(lats), len(lons)), dtype=bool)
    shapes = [(polygon, 1)]
    transform = rasterio.transform.from_bounds(lons.min(), lats.min(), lons.max(), lats.max(), len(lons), len(lats))
    mask = rasterio.features.rasterize(shapes, out_shape=mask.shape, transform=transform)
    
    # Debug mask information
    with st.expander("Mask Information", expanded=False):
        st.write("Mask has data points:", mask.any())
    
    if not mask.any():
        st.warning("The mask did not capture any data points. The polygon might be too small or misaligned with the data grid.")
        return None
    
    # Convert mask to DataArray
    mask_da = xr.DataArray(mask, dims=("lat", "lon"), coords={"lat": lats, "lon": lons})
    
    # Check if years exist in the dataset
    available_years = ds.time.dt.year.values
    if year1 not in available_years:
        st.warning(f"Year {year1} not found in the dataset. Available years: {sorted(set(available_years))}")
        return None
    if year2 not in available_years:
        st.warning(f"Year {year2} not found in the dataset. Available years: {sorted(set(available_years))}")
        return None
    
    # Filter dataset by years
    year1_data = ds.sel(time=ds.time.dt.year == year1).groupby("time.month").mean("time")
    year2_data = ds.sel(time=ds.time.dt.year == year2).groupby("time.month").mean("time")
    
    # Debug data shapes
    with st.expander("Data Shapes", expanded=False):
        st.write(f"Data for {year1} shape:", year1_data.t.shape)
        st.write(f"Data for {year2} shape:", year2_data.t.shape)
    
    # Apply mask and average
    year1_temps = year1_data.t.where(mask_da).mean(dim=["lat", "lon"])
    year2_temps = year2_data.t.where(mask_da).mean(dim=["lat", "lon"])
    
    # Debug averaged temperatures
    with st.expander("Averaged Temperatures", expanded=False):
        st.write(f"Averaged Temperatures for {year1}:", year1_temps.values)
        st.write(f"Averaged Temperatures for {year2}:", year2_temps.values)
    
    # Compute temperature change
    temp_change = year2_temps - year1_temps
    
    # Apply additional warming if warming_degree > 1
    if warming_degree > 1:
        additional_warming = np.random.normal(loc=1 + (warming_degree - 2), scale=1, size=temp_change.shape)
        temp_change += additional_warming
        year2_temps += additional_warming
    
    # Check for NaN values
    if np.any(np.isnan(year1_temps)) or np.any(np.isnan(year2_temps)):
        st.warning("Temperature data contains NaN values. This might indicate missing data in the selected region or years.")
    
    # Prepare output
    result = {
        "year1": {month: float(temp) if not np.isnan(temp) else "N/A" for month, temp in zip(year1_temps.month.values, year1_temps.values)},
        "year2": {month: float(temp) if not np.isnan(temp) else "N/A" for month, temp in zip(year2_temps.month.values, year2_temps.values)},
        "change": {month: float(diff) if not np.isnan(diff) else "N/A" for month, diff in zip(temp_change.month.values, temp_change.values)},
    }
    
    return result

# Function to create temperature comparison chart
def create_temperature_chart(df, year1, year2):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set dark background style for the chart
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a192f')
    ax.set_facecolor('#0a192f')
    
    # Plot lines
    ax.plot(df['Month'], df[f'Temperature {year1} (°C)'], marker='o', linewidth=3, color='#64ffda', label=f'{year1}')
    ax.plot(df['Month'], df[f'Temperature {year2} (°C)'], marker='o', linewidth=3, color='#ff5a5f', label=f'{year2}')
    
    # Customize grid
    ax.grid(color='#8892b0', linestyle='--', linewidth=0.5, alpha=0.3)
    
    # Add labels and title
    ax.set_xlabel('Month', fontsize=12, color='#ccd6f6')
    ax.set_ylabel('Temperature (°C)', fontsize=12, color='#ccd6f6')
    ax.set_title(f'Monthly Temperature Comparison: {year1} vs {year2}', fontsize=16, color='#64ffda')
    
    # Customize tick labels
    ax.tick_params(axis='x', colors='#8892b0')
    ax.tick_params(axis='y', colors='#8892b0')
    
    # Add legend
    legend = ax.legend(fontsize=12)
    for text in legend.get_texts():
        text.set_color('#e6f1ff')
    
    # Add subtle glow effect to lines
    for line in ax.get_lines():
        line.set_path_effects([PathEffects.withStroke(linewidth=5, foreground='#64ffda', alpha=0.3)])
    
    plt.tight_layout()
    return fig

# Function to create temperature change chart
def create_change_chart(df):
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Set dark background style for the chart
    plt.style.use('dark_background')
    fig.patch.set_facecolor('#0a192f')
    ax.set_facecolor('#0a192f')
    
    # Create bars with color based on values (positive = red, negative = blue)
    bars = ax.bar(df['Month'], df['Change (°C)'], color=['#ff5a5f' if x > 0 else '#64ffda' for x in df['Change (°C)']])
    
    # Add value labels above bars
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            y_pos = height + 0.1
        else:
            y_pos = height - 0.6
        ax.text(bar.get_x() + bar.get_width()/2., y_pos,
                f'{height:.1f}°C', ha='center', color='#e6f1ff', fontsize=10)
    
    # Add a horizontal line at y=0
    ax.axhline(y=0, color='#8892b0', linestyle='-', alpha=0.5)
    
    # Customize grid
    ax.grid(color='#8892b0', linestyle='--', linewidth=0.5, alpha=0.3)
    
    # Add labels and title
    ax.set_xlabel('Month', fontsize=12, color='#ccd6f6')
    ax.set_ylabel('Temperature Change (°C)', fontsize=12, color='#ccd6f6')
    ax.set_title('Monthly Temperature Change', fontsize=16, color='#64ffda')
    
    # Customize tick labels
    ax.tick_params(axis='x', colors='#8892b0')
    ax.tick_params(axis='y', colors='#8892b0')
    
    plt.tight_layout()
    return fig

# Sidebar Configuration
st.sidebar.markdown('<div class="sidebar-header"><h3>🌍 Analysis Settings</h3></div>', unsafe_allow_html=True)

# NetCDF file path
netcdf_path = r"C:\Users\joshd\Documents\Programming\HKSPRK\datasets\temperature_avg.nc"  # Replace with your actual path
if not os.path.exists(netcdf_path):
    st.error(f"NetCDF file not found at {netcdf_path}. Please check the path.")
    st.stop()

# Load dataset to get available years
try:
    ds = xr.open_dataset(netcdf_path)
    available_years = ds.time.dt.year.values
    available_years = sorted(list(set(available_years)))  # Unique years
except Exception as e:
    st.error(f"Error loading NetCDF file: {str(e)}")
    st.stop()

# Year selection
st.sidebar.markdown('<div class="sidebar-header"><h3>📅 Time Period</h3></div>', unsafe_allow_html=True)
year1 = st.sidebar.selectbox("Select Start Year", available_years, index=0)
year2 = st.sidebar.selectbox("Select End Year", available_years, index=len(available_years)-1)

# Warming degree selection
st.sidebar.markdown('<div class="sidebar-header"><h3>🔥 Warming Settings</h3></div>', unsafe_allow_html=True)
warming_degree = st.sidebar.slider("Select Warming Degree", 1.0, 5.0, 1.0, step=0.1, 
                                 help="Adjust the degree of warming to apply beyond natural warming")

# Display summary cards
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
        <div class="temp-box">
            <h3 style="color: #64ffda; margin-bottom: 10px;">Base Year</h3>
            <p style="font-size: 32px; font-weight: bold; color: #e6f1ff;">{}</p>
        </div>
    """.format(year1), unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="temp-box">
            <h3 style="color: #64ffda; margin-bottom: 10px;">Comparison Year</h3>
            <p style="font-size: 32px; font-weight: bold; color: #e6f1ff;">{}</p>
        </div>
    """.format(year2), unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="temp-box">
            <h3 style="color: #ff5a5f; margin-bottom: 10px;">Warming Degree</h3>
            <p style="font-size: 32px; font-weight: bold; color: #e6f1ff;">{}°C</p>
        </div>
    """.format(warming_degree), unsafe_allow_html=True)

# Create Folium map with OSM tiles for drawing
st.subheader("🗺️ Select Region of Interest")
st.markdown("""
    <p style="color: #8892b0; margin-bottom: 20px;">
        Draw a polygon on the map below, then click 'Export' to save it as a GeoJSON file.
    </p>
""", unsafe_allow_html=True)

m = folium.Map(location=[18.5204, 73.8567], zoom_start=10)  # Dark theme retained
draw = Draw(
    export=True,
    draw_options={"polygon": True, "polyline": False, "rectangle": False, "circle": False, "marker": False}
)
m.add_child(draw)

# Display map
folium_static(m)

# Function to display charts and results
def display_temperature_results(result, year1, year2):
    months = range(1, 13)
    month_names = [get_month_name(m) for m in months]  # Convert to month names
    
    data = {
        "Month": month_names,
        f"Temperature {year1} (°C)": [result["year1"].get(m, "N/A") for m in months],
        f"Temperature {year2} (°C)": [result["year2"].get(m, "N/A") for m in months],
        "Change (°C)": [result["change"].get(m, "N/A") for m in months]
    }
    df = pd.DataFrame(data)
    
    # Display charts
    st.subheader("📈 Temperature Visualization")
    
    # Temperature comparison chart
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    temp_fig = create_temperature_chart(df, year1, year2)
    st.pyplot(temp_fig)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Temperature change chart
    st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
    change_fig = create_change_chart(df)
    st.pyplot(change_fig)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display table with data
    st.subheader("📊 Monthly Temperature Analysis")
    st.table(df)

# Option to test with predefined Pune bounds
if st.button("Test with Predefined Pune Bounds"):
    pune_bbox = box(73.5, 18.3, 74.2, 18.8)  # Same as test case
    with st.spinner("Calculating temperature change with predefined Pune bounds..."):
        result = extract_temperature_change(netcdf_path, pune_bbox, year1, year2, warming_degree)
    if result:
        display_temperature_results(result, year1, year2)

# File uploader for GeoJSON with white text
st.markdown('<h2 id="-upload-region-data" style="color: #ffffff;">📤 Upload Region Data</h2>', unsafe_allow_html=True)
st.markdown('<p style="color: #ffffff;">Upload the exported GeoJSON file to analyze temperature changes.</p>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload the exported GeoJSON file", type=["geojson"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("temp_polygon.geojson", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Load GeoJSON and process
    try:
        with open("temp_polygon.geojson", "r") as f:
            geojson = json.load(f)
        
        # Extract coordinates (assuming single polygon)
        coords = geojson["features"][0]["geometry"]["coordinates"]
        polygon = shape(geojson["features"][0]["geometry"])  # Convert to shapely polygon
        
        # Calculate temperature change
        with st.spinner("Calculating temperature change..."):
            result = extract_temperature_change(netcdf_path, polygon, year1, year2, warming_degree)
        
        if result is None:
            st.error("Temperature calculation failed. See debug output for details.")
        else:
            display_temperature_results(result, year1, year2)
        
        # Clean up temporary file
        os.remove("temp_polygon.geojson")
    
    except Exception as e:
        st.error(f"Error processing GeoJSON or calculating temperature change: {str(e)}")
        if os.path.exists("temp_polygon.geojson"):
            os.remove("temp_polygon.geojson")

else:
    st.markdown('<div style="color: #ffffff;">Please upload the GeoJSON file after drawing and exporting your polygon.</div>', unsafe_allow_html=True)

# Footer with enhanced styling
st.markdown("""
    <footer>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 10px;">
            <p>🌡️ Climate Analysis Tool | Built with Streamlit & NetCDF Data</p>
            <p style="font-size: 14px; color: #64ffda;">Understanding our changing climate, one region at a time.</p>
        </div>
    </footer>
""", unsafe_allow_html=True)
