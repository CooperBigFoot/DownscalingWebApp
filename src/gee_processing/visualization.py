import ee
import geemap
import folium
from typing import Dict, List, Union
import matplotlib.pyplot as plt


def create_map(center: List[float], zoom: int = 9) -> geemap.Map:
    """
    Creates a geemap Map object centered on the given coordinates.

    Args:
        center (List[float]): Center coordinates [longitude, latitude].
        zoom (int): Initial zoom level. Default is 9.

    Returns:
        geemap.Map: A geemap Map object.
    """
    return geemap.Map(center=center, zoom=zoom)


def add_ee_layer(
    map_obj: geemap.Map,
    ee_object: Union[ee.Image, ee.ImageCollection, ee.FeatureCollection],
    vis_params: Dict,
    name: str,
) -> geemap.Map:
    """
    Adds an Earth Engine layer to a geemap Map object.

    Args:
        map_obj (geemap.Map): The map object to add the layer to.
        ee_object (Union[ee.Image, ee.ImageCollection, ee.FeatureCollection]): The EE object to display.
        vis_params (Dict): Visualization parameters for the layer.
        name (str): Name of the layer.

    Returns:
        geemap.Map: The updated map object.
    """
    map_obj.addLayer(ee_object, vis_params, name)
    return map_obj


def add_colorbar(
    map_obj: geemap.Map,
    vis_params: Dict,
    label: str,
    orientation: str = "horizontal",
    position: str = "bottom",
) -> geemap.Map:
    """
    Adds a colorbar to the map.

    Args:
        map_obj (geemap.Map): The map object to add the colorbar to.
        vis_params (Dict): Visualization parameters containing 'min', 'max', and 'palette'.
        label (str): Label for the colorbar.
        orientation (str): Orientation of the colorbar. Default is "horizontal".
        position (str): Position of the colorbar. Default is "bottom".

    Returns:
        geemap.Map: The updated map object.
    """
    map_obj.add_colorbar(
        vis_params=vis_params,
        label=label,
        orientation=orientation,
        position=position,
    )
    return map_obj


def create_ndvi_vis_params(min_value: float = -1, max_value: float = 1) -> Dict:
    """
    Creates visualization parameters for NDVI.

    Args:
        min_value (float): Minimum value for NDVI. Default is -1.
        max_value (float): Maximum value for NDVI. Default is 1.

    Returns:
        Dict: Visualization parameters for NDVI.
    """
    return {
        "min": min_value,
        "max": max_value,
        "palette": ["blue", "white", "green"],
    }


def create_lst_vis_params(min_value: float, max_value: float) -> Dict:
    """
    Creates visualization parameters for LST.

    Args:
        min_value (float): Minimum value for LST.
        max_value (float): Maximum value for LST.

    Returns:
        Dict: Visualization parameters for LST.
    """
    return {
        "min": min_value,
        "max": max_value,
        "palette": [
            "040274",
            "040281",
            "0502a3",
            "0502b8",
            "0502ce",
            "0502e6",
            "0602ff",
            "235cb1",
            "307ef3",
            "269db1",
            "30c8e2",
            "32d3ef",
            "3be285",
            "3ff38f",
            "86e26f",
            "3ae237",
            "b5e22e",
            "d6e21f",
            "fff705",
            "ffd611",
            "ffb613",
            "ff8b13",
            "ff6e08",
            "ff500d",
            "ff0000",
            "de0101",
            "c21301",
            "a71001",
            "911003",
        ],
    }


def create_scatter_plot(
    x: ee.Array, y: ee.Array, x_label: str, y_label: str, title: str
) -> plt.Figure:
    """
    Creates a scatter plot using Earth Engine arrays.

    Args:
        x (ee.Array): Array of x-values.
        y (ee.Array): Array of y-values.
        x_label (str): Label for x-axis.
        y_label (str): Label for y-axis.
        title (str): Title of the plot.

    Returns:
        plt.Figure: A matplotlib Figure object containing the scatter plot.
    """
    # Sample points from the image
    points = ee.FeatureCollection.randomPoints(ROI, 1000)
    values = x.addBands(y).reduceRegion(
        reducer=ee.Reducer.toList(), geometry=points, scale=30, maxPixels=1e9
    )

    x_values = values.get(x.bandNames().get(0)).getInfo()
    y_values = values.get(y.bandNames().get(0)).getInfo()

    fig, ax = plt.subplots()
    ax.scatter(x_values, y_values, alpha=0.5)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title)

    return fig


def visualize_downscaling_results(
    original_lst: ee.Image,
    downscaled_lst: ee.Image,
    region: ee.Geometry,
    center: List[float],
    zoom: int = 12,
) -> geemap.Map:
    """
    Visualizes the original and downscaled LST results on a map.

    Args:
        original_lst (ee.Image): Original Landsat LST image.
        downscaled_lst (ee.Image): Downscaled LST image.
        region (ee.Geometry): Region of interest.
        center (List[float]): Center coordinates [longitude, latitude] for the map.
        zoom (int): Initial zoom level. Default is 12.

    Returns:
        geemap.Map: A geemap Map object with the visualization layers.
    """
    map_obj = create_map(center, zoom)

    # Get LST range for visualization
    lst_range = original_lst.reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=region,
        scale=30,
        maxPixels=1e9,
    )
    min_lst = lst_range.get("LST_min").getInfo()
    max_lst = lst_range.get("LST_max").getInfo()

    lst_vis_params = create_lst_vis_params(min_lst, max_lst)

    # Add layers to the map
    map_obj = add_ee_layer(map_obj, original_lst, lst_vis_params, "Original LST (30m)")
    map_obj = add_ee_layer(
        map_obj, downscaled_lst, lst_vis_params, "Downscaled LST (10m)"
    )

    # Add a colorbar
    map_obj = add_colorbar(map_obj, lst_vis_params, "Land Surface Temperature (°C)")

    return map_obj
