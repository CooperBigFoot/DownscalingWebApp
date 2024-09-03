import ee
from typing import Dict, Callable

# Define band mappings for different sensors.
# Source: https://developers.google.com/earth-engine/datasets/catalog/landsat-8
# Source: https://developers.google.com/earth-engine/datasets/catalog/sentinel-2
BAND_MAPPINGS = {
    "landsat": {"nir": "SR_B5", "red": "SR_B4", "swir1": "SR_B6", "green": "SR_B3"},
    "sentinel2": {"nir": "B8", "red": "B4", "swir1": "B11", "green": "B3"},
}


def create_index_function(
    index_name: str, band1: str, band2: str
) -> Callable[[ee.Image, Dict[str, str]], ee.Image]:
    """
    Creates a function to calculate a specific spectral index.

    Args:
        index_name (str): Name of the index (e.g., 'NDVI').
        band1 (str): Key for the first band in BAND_MAPPINGS.
        band2 (str): Key for the second band in BAND_MAPPINGS.

    Returns:
        Callable: Function that calculates the index for a given image and band mapping.
    """

    def calculate_index(image: ee.Image, band_mapping: Dict[str, str]) -> ee.Image:
        return image.normalizedDifference(
            [band_mapping[band1], band_mapping[band2]]
        ).rename(index_name)

    return calculate_index


# Create index calculation functions
calculate_ndvi = create_index_function("NDVI", "nir", "red")
calculate_ndbi = create_index_function("NDBI", "swir1", "nir")
calculate_ndwi = create_index_function("NDWI", "green", "nir")


def calculate_indices(image: ee.Image, sensor: str) -> ee.Image:
    """
    Calculates NDVI, NDBI, and NDWI for the given image.

    Args:
        image (ee.Image): Input satellite image.
        sensor (str): Either 'landsat' or 'sentinel2'.

    Returns:
        ee.Image: Input image with added NDVI, NDBI, and NDWI bands.
    """
    band_mapping = BAND_MAPPINGS[sensor.lower()]

    ndvi = calculate_ndvi(image, band_mapping)
    ndbi = calculate_ndbi(image, band_mapping)
    ndwi = calculate_ndwi(image, band_mapping)

    return image.addBands([ndvi, ndbi, ndwi])


def add_indices_to_collection(
    collection: ee.ImageCollection, sensor: str
) -> ee.ImageCollection:
    """
    Adds spectral indices to all images in a collection.

    Args:
        collection (ee.ImageCollection): Input image collection.
        sensor (str): Either 'landsat' or 'sentinel2'.

    Returns:
        ee.ImageCollection: Image collection with added index bands.
    """
    if sensor.lower() not in BAND_MAPPINGS:
        raise ValueError("Sensor must be either 'landsat' or 'sentinel2'")

    return collection.map(lambda img: calculate_indices(img, sensor))
