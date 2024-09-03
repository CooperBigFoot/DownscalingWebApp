# File: /src/app.py

import streamlit as st
import geemap.foliumap as geemap
import datetime
import ee
from typing import Tuple
import pandas as pd
import altair as alt

# Import backend modules
from gee_processing.image_collection import (
    get_landsat_collection,
    get_sentinel2_collection,
    get_single_landsat_image,
    get_single_sentinel2_image,
)
from gee_processing.spectral_indices import add_indices_to_collection
from gee_processing.lst_calculation import (
    add_lst_to_collection,
    get_lst_parameters,
    calculate_lst,
)
from gee_processing.regression_model import create_ridge_regression_model
from gee_processing.downscaling import downscale_lst
from gee_processing.visualization import (
    create_map,
    add_ee_layer,
    create_lst_vis_params,
    visualize_downscaling_results,
    create_scatter_plot,
)

# Initialize Earth Engine
ee.Initialize(project="earth-engine-web-app")

# Define global variables
ROI = ee.Geometry.Rectangle(
    [21.134189623651263, 48.57888560664585, 21.433567065057513, 48.82947658234015]
)


def main():
    st.set_page_config(layout="wide", page_title="LST Downscaling")

    # Sidebar with controls and paper information
    start_date, end_date, landsat_collection, cloud_cover = create_sidebar()

    # Main content
    st.title("Land Surface Temperature Downscaling")

    display_about_section()

    # Create two columns: map and results
    col1, col2 = st.columns([2, 1])

    with col1:
        map_obj = create_map_view()
        map_placeholder = st.empty()
        map_placeholder.pydeck_chart(map_obj.to_streamlit(height=600))

    with col2:
        results_placeholder = st.empty()
        display_results(results_placeholder)

    # Process data and update map when the user clicks the button
    if st.sidebar.button("Generate Downscaled LST"):
        with st.spinner("Processing data..."):
            landsat_image, sentinel_image, downscaled_lst = process_data(
                start_date, end_date, landsat_collection, cloud_cover
            )
            if (
                landsat_image is None
                or sentinel_image is None
                or downscaled_lst is None
            ):
                st.error(
                    "Failed to process data. Please check the console for more information."
                )
            else:
                update_map(map_obj, landsat_image, sentinel_image, downscaled_lst)
                map_placeholder.pydeck_chart(map_obj.to_streamlit(height=600))


def create_sidebar() -> Tuple[datetime.date, datetime.date, str, float]:
    st.sidebar.title("LST Downscaling Controls")

    st.sidebar.header("1. Date Selection")
    start_date = st.sidebar.date_input("Start Date", datetime.date(2018, 8, 21))
    end_date = st.sidebar.date_input("End Date", datetime.date(2018, 8, 27))

    st.sidebar.header("2. Image Collection")
    landsat_collection = st.sidebar.selectbox(
        "Choose a Landsat Collection",
        ("LANDSAT/LC08/C02/T1_L2", "LANDSAT/LC09/C02/T1_L2"),
    )
    cloud_cover = st.sidebar.slider("Max Cloud Coverage (%)", 0, 100, 5)

    return start_date, end_date, landsat_collection, cloud_cover


def display_about_section():
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


def create_map_view() -> geemap.Map:
    st.subheader("Map View")
    map_obj = create_map(center=[21.2611, 48.7164], zoom=10)
    map_obj.add_basemap("HYBRID")
    return map_obj


def display_results(placeholder):
    placeholder.subheader("Analysis Results")
    placeholder.write("Charts and statistics will be displayed here after processing.")


def process_data(
    start_date: datetime.date,
    end_date: datetime.date,
    landsat_collection: str,
    cloud_cover: float,
) -> Tuple[ee.Image, ee.Image, ee.Image]:
    print(f"Processing data for date range: {start_date} to {end_date}")
    print(f"Landsat collection: {landsat_collection}")
    print(f"Cloud cover threshold: {cloud_cover}%")

    try:
        # Get Landsat and Sentinel-2 collections
        landsat_coll = get_landsat_collection(
            start_date.isoformat(),
            end_date.isoformat(),
            ROI,
            cloud_cover,
            landsat_collection,
        )
        sentinel_coll = get_sentinel2_collection(
            start_date.isoformat(), end_date.isoformat(), ROI, cloud_cover
        )

        print("Landsat collection size:", landsat_coll.size().getInfo())
        print("Sentinel-2 collection size:", sentinel_coll.size().getInfo())

        if landsat_coll.size().getInfo() == 0 or sentinel_coll.size().getInfo() == 0:
            raise ValueError(
                "No images found in the specified date range and cloud cover threshold."
            )

        # Add spectral indices to Landsat collection
        landsat_coll = add_indices_to_collection(landsat_coll, "landsat")
        print("Spectral indices added to Landsat collection")

        # Add LST to Landsat collection
        landsat_coll = add_lst_to_collection(landsat_coll)
        print("LST added to Landsat collection")

        # Get a single image from each collection
        landsat_image = get_single_landsat_image(
            landsat_coll, start_date.isoformat(), end_date.isoformat()
        )
        if landsat_image is None:
            raise ValueError("Failed to retrieve a valid Landsat image")

        # Use the same date range for Sentinel-2
        sentinel_image = get_single_sentinel2_image(
            sentinel_coll, start_date.isoformat(), end_date.isoformat()
        )
        if sentinel_image is None:
            raise ValueError("Failed to retrieve a valid Sentinel-2 image")

        # Print Landsat image bands for debugging
        print("Landsat image bands:", landsat_image.bandNames().getInfo())

        # Create regression model
        regression_coefficients = create_ridge_regression_model(
            landsat_image, "LST", ["NDVI", "NDBI", "NDWI"], ROI
        )

        # Downscale LST
        downscaled_lst = downscale_lst(
            sentinel_image,
            landsat_image,
            regression_coefficients,
            ["NDVI", "NDBI", "NDWI"],
        )

        return landsat_image, sentinel_image, downscaled_lst

    except Exception as e:
        print(f"An error occurred in process_data: {str(e)}")
        import traceback

        traceback.print_exc()
        return None, None, None


def update_map(
    map_obj: geemap.Map,
    landsat_image: ee.Image,
    sentinel_image: ee.Image,
    downscaled_lst: ee.Image,
):
    # Clear existing layers
    map_obj.layers = map_obj.layers[:1]  # Keep only the base layer

    try:
        # Get LST visualization parameters
        lst_params = get_lst_parameters(landsat_image)
        if lst_params["min"] is None or lst_params["max"] is None:
            st.warning("Unable to retrieve LST parameters. Using default values.")
            lst_params = {"min": 20, "max": 40}

        lst_vis_params = create_lst_vis_params(lst_params["min"], lst_params["max"])

        # Add layers to the map
        add_ee_layer(
            map_obj,
            landsat_image.select("LST"),
            lst_vis_params,
            "Landsat LST (30m)",
        )
        add_ee_layer(
            map_obj,
            downscaled_lst.select("LST_downscaled"),
            lst_vis_params,
            "Downscaled LST (10m)",
        )
        add_ee_layer(
            map_obj,
            sentinel_image.select(["B4", "B3", "B2"]),
            {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]},
            "Sentinel-2 RGB",
        )

        # Update the map center and zoom
        map_obj.center_object(ROI, 11)

        st.success("Map updated successfully")
    except Exception as e:
        st.error(f"Error updating map: {str(e)}")
        import traceback

        st.code(traceback.format_exc())


def update_results(
    placeholder,
    landsat_image: ee.Image,
    sentinel_image: ee.Image,
    downscaled_lst: ee.Image,
):
    placeholder.empty()
    placeholder.subheader("Analysis Results")

    if landsat_image is None or sentinel_image is None or downscaled_lst is None:
        placeholder.warning(
            "Unable to display results. Some required images are missing."
        )
        return

    try:
        # Sample points for creating charts
        sample_points = landsat_image.select(["NDVI", "NDBI", "NDWI", "LST"]).sample(
            region=ROI, scale=30, numPixels=500, seed=42
        )

        # Convert to pandas DataFrame
        sample_data = sample_points.getInfo()
        df = pd.DataFrame(
            [feature["properties"] for feature in sample_data["features"]]
        )

        # Create scatter plots
        placeholder.subheader("Spectral Indices vs LST")

        for index in ["NDVI", "NDBI", "NDWI"]:
            chart = (
                alt.Chart(df)
                .mark_circle()
                .encode(
                    x=alt.X(index, title=index),
                    y=alt.Y("LST", title="LST (°C)"),
                    tooltip=[index, "LST"],
                )
                .properties(width=400, height=300, title=f"LST vs {index}")
            )
            placeholder.altair_chart(chart, use_container_width=True)

        # Display statistics
        placeholder.subheader("LST Statistics")
        landsat_lst_stats = (
            landsat_image.select("LST")
            .reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), None, True),
                geometry=ROI,
                scale=30,
                maxPixels=1e9,
            )
            .getInfo()
        )

        downscaled_lst_stats = (
            downscaled_lst.select("LST_downscaled")
            .reduceRegion(
                reducer=ee.Reducer.mean().combine(ee.Reducer.stdDev(), None, True),
                geometry=ROI,
                scale=10,
                maxPixels=1e9,
            )
            .getInfo()
        )

        if "LST_mean" in landsat_lst_stats and "LST_stdDev" in landsat_lst_stats:
            placeholder.write(
                f"Landsat LST (30m): Mean = {landsat_lst_stats['LST_mean']:.2f}°C, Std Dev = {landsat_lst_stats['LST_stdDev']:.2f}°C"
            )
        else:
            placeholder.write("Landsat LST statistics are not available.")

        if (
            "LST_downscaled_mean" in downscaled_lst_stats
            and "LST_downscaled_stdDev" in downscaled_lst_stats
        ):
            placeholder.write(
                f"Downscaled LST (10m): Mean = {downscaled_lst_stats['LST_downscaled_mean']:.2f}°C, Std Dev = {downscaled_lst_stats['LST_downscaled_stdDev']:.2f}°C"
            )
        else:
            placeholder.write("Downscaled LST statistics are not available.")

    except Exception as e:
        placeholder.error(f"An error occurred while updating results: {str(e)}")
        import traceback

        placeholder.code(traceback.format_exc())


if __name__ == "__main__":
    main()
