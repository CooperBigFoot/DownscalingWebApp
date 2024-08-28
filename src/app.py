# File: src/ui/main_app.py

import streamlit as st
import geemap.foliumap as geemap
import datetime
import ee

# Initialize Earth Engine
ee.Initialize()


def main():
    st.set_page_config(layout="wide", page_title="LST Downscaling")

    # Sidebar with controls and paper information
    create_sidebar()

    # Main content
    st.title("Land Surface Temperature Downscaling")

    st.header("About")
    st.write(
        "This application is based on the methodology described in the following paper:"
    )
    st.markdown(
        """
    Onačillová, K.; Gallay, M.; Paluba, D.; Péliová, A.; Tokarčík, O.; Laubertová, D. 
    Combining Landsat 8 and Sentinel-2 Data in Google Earth Engine to Derive Higher Resolution 
    Land Surface Temperature Maps in Urban Environment. Remote Sens. 2022, 14, 4076.
    """
    )
    st.markdown(
        "[https://doi.org/10.3390/rs14164076](https://doi.org/10.3390/rs14164076)"
    )

    st.markdown("---")

    # Create two columns: map and results
    col1, col2 = st.columns([2, 1])

    with col1:
        create_map()

    with col2:
        display_results()


def create_sidebar():
    st.sidebar.title("LST Downscaling Controls")

    st.sidebar.header("1. Date Selection")
    start_date = st.sidebar.date_input("Start Date", datetime.date(2018, 8, 21))
    end_date = st.sidebar.date_input("End Date", datetime.date(2018, 8, 27))

    st.sidebar.markdown("---")

    st.sidebar.header("2. Image Collection")
    landsat_collection = st.sidebar.selectbox(
        "Choose a Landsat Collection",
        ("Landsat 8 Image Collection", "Landsat 9 Image Collection"),
    )
    cloud_cover = st.sidebar.slider("Max Cloud Coverage (%)", 0, 100, 5)

    if st.sidebar.button("Generate Image Collections"):
        # This would normally trigger the backend processing
        st.sidebar.success("Image collections generated!")

    st.sidebar.markdown("---")

    st.sidebar.header("3. Image Selection")
    landsat_ids = ["LC08_186026_20180823"]  # This would be dynamically populated
    sentinel_ids = [
        "20180823T094029_20180823T094320_T34UEU"
    ]  # This would be dynamically populated

    selected_landsat_id = st.sidebar.selectbox("Select Landsat Image", landsat_ids)
    selected_sentinel_id = st.sidebar.selectbox("Select Sentinel-2 Image", sentinel_ids)

    if st.sidebar.button("Generate Downscaled LST"):
        # This would normally trigger the LST downscaling process
        st.sidebar.success("Downscaled LST generated!")

    st.sidebar.markdown("---")

    st.sidebar.header("4. Layer Visibility")
    layers = [
        "LST 10 m with residuals",
        "LST 10 m (no residuals)",
        "Landsat 8/9 LST",
        "Landsat 8/9 LST regression residuals",
        "Sentinel-2 RGB",
        "Landsat 8/9 RGB",
        "ROI",
    ]
    layer_visibility = {
        layer: st.sidebar.checkbox(layer, value=layer == "LST 10 m with residuals")
        for layer in layers
    }

    st.sidebar.markdown("---")

    if st.sidebar.button("Generate Spectral Indices Charts"):
        # This would normally generate the charts
        st.sidebar.success("Charts generated!")

    st.sidebar.markdown("---")

def create_map():
    st.subheader("Map View")

    # Create and configure the map
    m = geemap.Map()
    m.setCenter(21.2611, 48.7164, 10)  # Centered on Košice, Slovakia

    # Here you would add the layers based on the processing results
    # For demonstration, let's add a sample TileLayer
    m.add_tile_layer(
        url="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        name="Google Satellite",
        attribution="Google",
    )

    # Display the map
    m.to_streamlit(height=600)

    # Add a color bar for LST
    st.write("Land Surface Temperature (°C)")
    st.image(
        "https://via.placeholder.com/500x50.png?text=LST+Color+Bar",
        use_column_width=True,
    )


def display_results():
    st.subheader("Analysis Results")
    st.write("Charts and statistics will be displayed here after processing.")

    # Placeholder for charts
    st.write("Correlation: LST vs NDVI")
    st.image("https://via.placeholder.com/400x300.png?text=LST+vs+NDVI+Chart")

    st.write("Correlation: LST vs NDBI")
    st.image("https://via.placeholder.com/400x300.png?text=LST+vs+NDBI+Chart")

    st.write("Correlation: LST vs NDWI")
    st.image("https://via.placeholder.com/400x300.png?text=LST+vs+NDWI+Chart")


if __name__ == "__main__":
    main()
