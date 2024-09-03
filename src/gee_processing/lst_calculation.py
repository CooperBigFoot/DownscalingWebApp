import ee
from typing import Dict, Union


def calculate_lst(image: ee.Image) -> ee.Image:
    """
    Calculates Land Surface Temperature (LST) for Landsat 8/9 imagery.
    """
    has_thermal_band = image.bandNames().contains("ST_B10")

    # Use ee.Algorithms.If to handle both cases
    return ee.Algorithms.If(
        has_thermal_band,
        # If the thermal band exists, calculate LST
        image.addBands(image.select("ST_B10").rename("LST")),
        # If the thermal band doesn't exist, return the original image
        image,
    )


def add_lst_to_collection(collection: ee.ImageCollection) -> ee.ImageCollection:
    """
    Adds LST band to all images in a Landsat collection.

    Args:
        collection (ee.ImageCollection): Input Landsat image collection.

    Returns:
        ee.ImageCollection: Image collection with added LST band.
    """
    return collection.map(calculate_lst)


def get_lst_parameters(image: ee.Image) -> Dict[str, Union[float, None]]:
    """
    Calculates min and max LST values for the image.

    Args:
        image (ee.Image): Input image with LST band.

    Returns:
        Dict[str, Union[float, None]]: Dictionary containing min and max LST values, or None if LST band is not present.
    """
    lst_stats = image.select("LST").reduceRegion(
        reducer=ee.Reducer.minMax(),
        geometry=image.geometry(),
        scale=30,
        maxPixels=1e9,
    )

    return {"min": lst_stats.get("LST_min"), "max": lst_stats.get("LST_max")}
