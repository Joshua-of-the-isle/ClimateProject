import ee
import folium
import streamlit as st
from folium.plugins import Draw
from streamlit_folium import folium_static
import json
import os

# Initialize Earth Engine
ee.Initialize(project="ee-coding--api-access")

def calculate_vegetation_loss(polygon, year1, year2):
    """Calculate NDVI-based vegetation loss."""
    def get_ndvi(year):
        if year < 2013:
            collection = ee.ImageCollection("LANDSAT/LT05/C02/T1_TOA")
            bands = ["B4", "B3"]
        else:
            collection = ee.ImageCollection("LANDSAT/LC08/C02/T1_TOA")
            bands = ["B5", "B4"]
        
        filtered = (collection
                    .filterBounds(polygon)
                    .filterDate(f"{year}-01-01", f"{year}-12-31"))
        
        if filtered.size().getInfo() == 0:
            st.warning(f"No images found for {year}.")
            return ee.Image(0)
        
        image = filtered.median()
        available_bands = image.bandNames().getInfo()
        st.write(f"Available bands for {year}: {available_bands}")
        
        if all(b in available_bands for b in bands):
            return image.normalizedDifference(bands).rename("NDVI")
        else:
            st.warning(f"Missing bands for {year}.")
            return ee.Image(0)
    
    ndvi_year1 = get_ndvi(year1)
    ndvi_year2 = get_ndvi(year2)
    ndvi_diff = ndvi_year1.subtract(ndvi_year2)
    
    # Clip the NDVI difference to the polygon
    ndvi_diff_clipped = ndvi_diff.clip(polygon)
    
    loss_stats = ndvi_diff_clipped.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=polygon,
        scale=60,
        maxPixels=5e5
    )
    
    ndvi_value = loss_stats.get("NDVI")
    if ndvi_value is None:
        st.warning("No valid NDVI values found.")
        return {"Vegetation Loss (NDVI)": None}, ndvi_diff_clipped
    
    return {"Vegetation Loss (NDVI)": ndvi_value.getInfo()}, ndvi_diff_clipped

# Streamlit app
st.title("Vegetation Loss Calculator")

# Year selection
year1 = st.selectbox("Select Start Year", list(range(1995, 2014)), index=0)
year2 = st.selectbox("Select End Year", list(range(2013, 2025)), index=10)

# Create Folium map with OSM tiles for drawing
m = folium.Map(location=[19.0760, 72.8777], zoom_start=10, tiles="OpenStreetMap")
draw = Draw(
    export=True,
    draw_options={"polygon": True, "polyline": False, "rectangle": False, "circle": False, "marker": False}
)
m.add_child(draw)

# Display map
st.write("Draw a polygon on the map below, then click 'Export' to save it as a GeoJSON file.")
folium_static(m)

# File uploader for GeoJSON
uploaded_file = st.file_uploader("Upload the exported GeoJSON file", type=["geojson"])

if uploaded_file is not None:
    # Save the uploaded file temporarily
    with open("temp_polygon.geojson", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Load GeoJSON and process
    with open("temp_polygon.geojson", "r") as f:
        geojson = json.load(f)
    
    # Extract coordinates (assuming single polygon)
    coords = geojson["features"][0]["geometry"]["coordinates"]
    drawn_polygon = ee.Geometry.Polygon(coords)
    
    # Calculate vegetation loss
    with st.spinner("Calculating vegetation loss..."):
        vegetation_loss, ndvi_diff_clipped = calculate_vegetation_loss(drawn_polygon, year1, year2)
    
    # Display numerical result
    st.subheader("Vegetation Loss Result")
    st.write(vegetation_loss)
    
    # Debug NDVI difference range
    ndvi_range = ndvi_diff_clipped.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=drawn_polygon,
        scale=60,
        maxPixels=5e5
    ).getInfo()
    st.write("NDVI Difference Range:", ndvi_range)
    
    # Adjust visualization parameters based on range
    ndvi_min = ndvi_range.get("NDVI_min", -0.5)
    ndvi_max = ndvi_range.get("NDVI_max", 0.5)
    vis_params = {
        "min": max(ndvi_min, -0.5),
        "max": min(ndvi_max, 0.5),
        "palette": ["red", "yellow", "green"]
    }
    map_id = ndvi_diff_clipped.getMapId(vis_params)
    image_url = map_id["tile_fetcher"].url_format
    st.write("Tile URL:", image_url)  # Debug the URL
    
    # Get dynamic bounds from the polygon
    bounds = drawn_polygon.bounds().getInfo()["coordinates"][0]
    folium_bounds = [[bounds[0][1], bounds[0][0]], [bounds[2][1], bounds[2][0]]]  # [sw, ne]
    st.write("Calculated Bounds:", folium_bounds)  # Debug bounds
    
    # Create a new map for the result with OSM tiles
    result_map = folium.Map(location=[(bounds[0][1] + bounds[2][1]) / 2, (bounds[0][0] + bounds[2][0]) / 2],
                           zoom_start=10, tiles="OpenStreetMap")
    
    # Use TileLayer with clipped image
    folium.TileLayer(
        tiles=image_url,
        attr="Google Earth Engine",
        name="NDVI Difference",
        overlay=True,
        control=True,
        opacity=0.8
    ).add_to(result_map)
    
    # Add layer control
    folium.LayerControl().add_to(result_map)
    
    st.subheader("NDVI Difference Heatmap")
    folium_static(result_map)
    
    # Clean up temporary file
    os.remove("temp_polygon.geojson")

else:
    st.info("Please upload the GeoJSON file after drawing and exporting your polygon.")