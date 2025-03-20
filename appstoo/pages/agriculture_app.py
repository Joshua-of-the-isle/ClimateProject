import os
import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import folium_static
import json
import rasterio
import numpy as np
from shapely.geometry import Polygon, shape
import geopandas as gpd
from rasterio.mask import mask
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
import pandas as pd

# Functions from your code
def list_available_files(directory):
    """List all TIFF files in the given directory following the naming convention crop_rcp_year.tif."""
    files = [f for f in os.listdir(directory) if f.endswith(".tif")]
    metadata = []
    for file in files:
        parts = file.replace(".tif", "").split("_")
        if len(parts) == 3:
            crop, rcp, year = parts
            metadata.append((file, crop, float(rcp), int(year)))
    return metadata

def load_raster(file_path):
    """Load raster data and replace NoData values with 0."""
    with rasterio.open(file_path) as src:
        data = src.read(1).astype(float)  # Ensure data is float before replacing NoData values
        data[data == -9] = 0  # Replace NoData values with 0
        transform = src.transform
    return data, transform

def mask_raster_with_polygon(file_path, polygon):
    """Extract yield data within the given polygon."""
    with rasterio.open(file_path) as src:
        out_image, out_transform = mask(src, [polygon], crop=True)
        out_image = out_image[0].astype(float)  # Ensure data is float before modifying
        out_image[out_image == -9] = 0  # Replace NoData values with 0
    return out_image

def compute_average_yield(raster):
    """Compute average yield per hectare, treating NaN values as 0."""
    raster = np.nan_to_num(raster, nan=0)  # Convert NaNs to 0
    return np.mean(raster)

def interpolate_yield(directory, target_rcp, target_year, polygon):
    """Estimate the yield for all crops, RCP, and year using interpolation, considering an area."""
    files = list_available_files(directory)
    if not files:
        st.error("No TIFF files found in the directory matching the naming convention 'crop_rcp_year.tif'.")
        return None
    
    crops = set(f[1] for f in files)
    results = {}
    
    for crop in crops:
        crop_files = [f for f in files if f[1] == crop]
        years = sorted(set(f[3] for f in crop_files))
        rcps = sorted(set(f[2] for f in crop_files))
        
        # Debug: Display available years and RCPs for this crop
        st.write(f"Crop: {crop}, Available Years: {years}, Available RCPs: {rcps}")
        
        # Find bracketing years and RCPs
        lower_year = max(y for y in years if y <= target_year) if any(y <= target_year for y in years) else min(years)
        upper_year = min(y for y in years if y >= target_year) if any(y >= target_year for y in years) else max(years)
        lower_rcp = max(r for r in rcps if r <= target_rcp) if any(r <= target_rcp for r in rcps) else min(rcps)
        upper_rcp = min(r for r in rcps if r >= target_rcp) if any(r >= target_rcp for r in rcps) else max(rcps)
        
        def get_raster(crop, rcp, year):
            file_name = f"{crop}_{rcp}_{year}.tif"
            file_path = os.path.join(directory, file_name)
            if not os.path.exists(file_path):
                st.warning(f"File {file_name} not found. Skipping...")
                return np.zeros((100, 100))  # Dummy array to avoid errors
            raster = mask_raster_with_polygon(file_path, polygon)
            return raster
        
        lower_raster = get_raster(crop, lower_rcp, lower_year)
        upper_raster = get_raster(crop, upper_rcp, upper_year)
        
        # Interpolate over years
        if lower_year != upper_year:
            interp_func = interp1d([lower_year, upper_year], np.stack([lower_raster, upper_raster]), axis=0, fill_value="extrapolate")
            interpolated_raster = interp_func(target_year)
        else:
            interpolated_raster = lower_raster
        
        # Interpolate over RCPs
        if lower_rcp != upper_rcp:
            interp_func = interp1d([lower_rcp, upper_rcp], np.stack([lower_raster, upper_raster]), axis=0, fill_value="extrapolate")
            final_raster = interp_func(target_rcp)
        else:
            final_raster = interpolated_raster
        
        avg_yield = compute_average_yield(final_raster)
        results[crop] = avg_yield
    
    return results

st.markdown("""<style>        
            @media print {
            body {
                background-color: #1e1e2f !important;
                color: white !important;
            }
            .stApp {
                background-color: #1e1e2f !important;
            }
            table, th, td {
                color: white !important;
            }
        }</style>""",unsafe_allow_html=True)

# Streamlit app
st.title("Crop Yield Change Analyzer (Dynamic Data)")

# Directory path for TIFF files
directory = r"C:\Users\joshd\Documents\Programming\HKSPRK\crop"  # Replace with your actual path
if not os.path.exists(directory):
    st.error(f"Directory not found at {directory}. Please check the path.")
    st.stop()

# List available files and extract years and RCPs
files = list_available_files(directory)
if not files:
    st.error("No TIFF files found in the directory. Please add files with the naming convention 'crop_rcp_year.tif'.")
    st.stop()

available_years = sorted(set(f[3] for f in files))
available_rcps = sorted(set(f[2] for f in files))
crops = sorted(set(f[1] for f in files))

# Year selection
year1 = st.selectbox("Select Start Year", available_years, index=0)
year2 = st.selectbox("Select End Year", available_years, index=len(available_years)-1)

# RCP scenario selection
rcp_selected = st.selectbox("Select RCP Scenario", available_rcps, index=len(available_rcps)-1)

# Create Folium map with OSM tiles for drawing
m = folium.Map(location=[26.5, 80.0], zoom_start=6, tiles="OpenStreetMap")  # Centered on North India
draw = Draw(
    export=True,
    draw_options={"polygon": True, "polyline": False, "rectangle": False, "circle": False, "marker": False}
)
m.add_child(draw)

# Display map
st.write("Draw a polygon on the map below (covering North India), then click 'Export' to save it as a GeoJSON file.")
folium_static(m)

# Option to test with predefined North India polygon
if st.button("Test with Predefined North India Polygon"):
    coordinates = [
        (74.0, 30.0),  # Punjab
        (78.0, 30.0),  # Haryana
        (81.0, 30.0),  # Uttarakhand
        (87.0, 28.0),  # Bihar
        (88.0, 26.0),  # West Bengal
        (83.0, 25.0),  # Uttar Pradesh
        (75.0, 25.0),  # Rajasthan
        (74.0, 30.0)   # Closing the loop
    ]
    polygon = Polygon(coordinates)
    
    with st.spinner("Calculating yields with predefined North India polygon..."):
        yields_year1 = interpolate_yield(directory, target_rcp=rcp_selected, target_year=year1, polygon=polygon)
        yields_year2 = interpolate_yield(directory, target_rcp=rcp_selected, target_year=year2, polygon=polygon)
    
    if yields_year1 and yields_year2:
        # Prepare data for visualization
        crops = sorted(set(yields_year1.keys()) & set(yields_year2.keys()))
        yields1 = [yields_year1[crop] for crop in crops]
        yields2 = [yields_year2[crop] for crop in crops]
        percent_changes = [
            ((yields2[i] - yields1[i]) / yields1[i] * 100) if yields1[i] != 0 else 0
            for i in range(len(crops))
        ]

        # Create bar chart for yields
        st.subheader(f"Crop Yield Comparison (RCP {rcp_selected}, {year1} to {year2})")
        fig1, ax1 = plt.subplots(figsize=(10, 6))

        bar_width = 0.35
        index = np.arange(len(crops))

        bar1 = ax1.bar(index - bar_width/2, yields1, bar_width, label=f"Yield {year1} (kg/ha)", color='skyblue')
        bar2 = ax1.bar(index + bar_width/2, yields2, bar_width, label=f"Yield {year2} (kg/ha)", color='lightgreen')

        ax1.set_xlabel("Crops")
        ax1.set_ylabel("Yield (kg/ha)")
        ax1.set_title(f"Crop Yield Comparison (RCP {rcp_selected})")
        ax1.set_xticks(index)
        ax1.set_xticklabels(crops)
        ax1.legend()

        plt.tight_layout()
        st.pyplot(fig1)

        # Create separate bar chart for percentage change
        st.subheader(f"Percentage Change in Crop Yield (RCP {rcp_selected}, {year1} to {year2})")
        fig2, ax2 = plt.subplots(figsize=(10, 6))

        bars = ax2.bar(index, percent_changes, color='salmon')

        ax2.set_xlabel("Crops")
        ax2.set_ylabel("Percentage Change (%)")
        ax2.set_title(f"Percentage Change in Crop Yield (RCP {rcp_selected})")
        ax2.set_xticks(index)
        ax2.set_xticklabels(crops)

        # Add percentage labels on top of bars
        for bar in bars:
            yval = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.5 if yval >= 0 else yval - 2, f"{yval:.2f}%", ha='center', va='bottom' if yval >= 0 else 'top')

        plt.tight_layout()
        st.pyplot(fig2)

        # Display data in a table
        st.subheader("Crop Yield Details")
        data = {
            "Crop": crops,
            f"Yield {year1} (kg/ha)": yields1,
            f"Yield {year2} (kg/ha)": yields2,
            "Percentage Change (%)": percent_changes
        }
        df = pd.DataFrame(data)
        st.table(df)

# File uploader for GeoJSON
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
        polygon = shape(geojson["features"][0]["geometry"])  # Convert to shapely polygon
        
        # Calculate yields for both years
        with st.spinner("Calculating yields..."):
            yields_year1 = interpolate_yield(directory, target_rcp=rcp_selected, target_year=year1, polygon=polygon)
            yields_year2 = interpolate_yield(directory, target_rcp=rcp_selected, target_year=year2, polygon=polygon)
        
        if yields_year1 and yields_year2:
            # Prepare data for visualization
            crops = sorted(set(yields_year1.keys()) & set(yields_year2.keys()))
            yields1 = [yields_year1[crop] for crop in crops]
            yields2 = [yields_year2[crop] for crop in crops]
            percent_changes = [
                ((yields2[i] - yields1[i]) / yields1[i] * 100) if yields1[i] != 0 else 0
                for i in range(len(crops))
            ]

            # Create bar chart for yields
            st.subheader(f"Crop Yield Comparison (RCP {rcp_selected}, {year1} to {year2})")
            fig1, ax1 = plt.subplots(figsize=(10, 6))

            bar_width = 0.35
            index = np.arange(len(crops))

            bar1 = ax1.bar(index - bar_width/2, yields1, bar_width, label=f"Yield {year1} (kg/ha)", color='skyblue')
            bar2 = ax1.bar(index + bar_width/2, yields2, bar_width, label=f"Yield {year2} (kg/ha)", color='lightgreen')

            ax1.set_xlabel("Crops")
            ax1.set_ylabel("Yield (kg/ha)")
            ax1.set_title(f"Crop Yield Comparison (RCP {rcp_selected})")
            ax1.set_xticks(index)
            ax1.set_xticklabels(crops)
            ax1.legend()

            plt.tight_layout()
            st.pyplot(fig1)

            # Create separate bar chart for percentage change
            st.subheader(f"Percentage Change in Crop Yield (RCP {rcp_selected}, {year1} to {year2})")
            fig2, ax2 = plt.subplots(figsize=(10, 6))

            bars = ax2.bar(index, percent_changes, color='salmon')

            ax2.set_xlabel("Crops")
            ax2.set_ylabel("Percentage Change (%)")
            ax2.set_title(f"Percentage Change in Crop Yield (RCP {rcp_selected})")
            ax2.set_xticks(index)
            ax2.set_xticklabels(crops)

            # Add percentage labels on top of bars
            for bar in bars:
                yval = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.5 if yval >= 0 else yval - 2, f"{yval:.2f}%", ha='center', va='bottom' if yval >= 0 else 'top')

            plt.tight_layout()
            st.pyplot(fig2)

            # Display data in a table
            st.subheader("Crop Yield Details")
            data = {
                "Crop": crops,
                f"Yield {year1} (kg/ha)": yields1,
                f"Yield {year2} (kg/ha)": yields2,
                "Percentage Change (%)": percent_changes
            }
            df = pd.DataFrame(data)
            st.table(df)
        
        # Clean up temporary file
        os.remove("temp_polygon.geojson")
    
    except Exception as e:
        st.error(f"Error processing GeoJSON or calculating yields: {str(e)}")
        if os.path.exists("temp_polygon.geojson"):
            os.remove("temp_polygon.geojson")

else:
    st.info("Please upload the GeoJSON file after drawing and exporting your polygon.")
