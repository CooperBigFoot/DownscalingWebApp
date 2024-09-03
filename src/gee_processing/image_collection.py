import ee


def get_landsat_collection(
    start_date: str,
    end_date: str,
    geometry: ee.Geometry,
    cloud_cover: float,
    collection: str = "LANDSAT/LC08/C02/T1_L2",
) -> ee.ImageCollection:
    """
    Retrieves and filters a Landsat 8 or 9 image collection.
    """
    landsat_collection = (
        ee.ImageCollection(collection)
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUD_COVER", cloud_cover))
    )

    # Print debug information
    print(f"Landsat collection size: {landsat_collection.size().getInfo()}")
    if landsat_collection.size().getInfo() > 0:
        print(f"First image ID: {landsat_collection.first().id().getInfo()}")

    return landsat_collection


def get_sentinel2_collection(
    start_date: str, end_date: str, geometry: ee.Geometry, cloud_cover: float
) -> ee.ImageCollection:
    """
    Retrieves and filters a Sentinel-2 image collection.

    Args:
        start_date (str): Start date for filtering (YYYY-MM-DD).
        end_date (str): End date for filtering (YYYY-MM-DD).
        geometry (ee.Geometry): Region of interest.
        cloud_cover (float): Maximum cloud cover percentage (0-100).

    Returns:
        ee.ImageCollection: Filtered Sentinel-2 image collection.
    """
    sentinel2_collection = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_cover))
    )

    return sentinel2_collection


def apply_scale_factors(image: ee.Image) -> ee.Image:
    """
    Applies scale factors to Landsat 8/9 Collection 2 images. The scale factors are as descibed here: https://www.usgs.gov/landsat-missions/landsat-collection-2-level-2-science-products.

    Args:
        image (ee.Image): Input Landsat image.

    Returns:
        ee.Image: Landsat image with scale factors applied.
    """
    optical_bands = image.select("SR_B.*").multiply(0.0000275).add(-0.2)
    thermal_bands = (
        image.select("ST_B.*").multiply(0.00341802).add(149.0).subtract(273.15)
    )
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)


def get_single_landsat_image(collection: ee.ImageCollection, start_date: str, end_date: str) -> ee.Image:
    """
    Retrieves a single Landsat image from a collection based on the given date range.
    """
    try:
        filtered_collection = collection.filterDate(start_date, end_date)
        image_count = filtered_collection.size().getInfo()
        print(f"Number of images found for date range {start_date} to {end_date}: {image_count}")

        if image_count == 0:
            print(f"No Landsat images found for date range: {start_date} to {end_date}")
            return None

        # Sort the collection by cloud cover and get the least cloudy image
        image = ee.Image(filtered_collection.sort('CLOUD_COVER').first())
        
        # Check if the image has bands
        band_names = image.bandNames().getInfo()
        if not band_names:
            print(f"Retrieved Landsat image has no bands for date range: {start_date} to {end_date}")
            return None

        image_date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        print(f"Retrieved Landsat image date: {image_date}")
        print(f"Retrieved Landsat image bands: {band_names}")
        return image
    except Exception as e:
        print(f"Error retrieving Landsat image: {str(e)}")
        return None


def get_single_sentinel2_image(collection: ee.ImageCollection, start_date: str, end_date: str) -> ee.Image:
    """
    Retrieves a single Sentinel-2 image from a collection based on the given date range.

    Args:
        collection (ee.ImageCollection): Sentinel-2 image collection.
        start_date (str): Start date for filtering (YYYY-MM-DD).
        end_date (str): End date for filtering (YYYY-MM-DD).

    Returns:
        ee.Image: Single Sentinel-2 image.
    """
    try:
        filtered_collection = collection.filterDate(start_date, end_date)
        image_count = filtered_collection.size().getInfo()
        print(f"Number of Sentinel-2 images found for date range {start_date} to {end_date}: {image_count}")

        if image_count == 0:
            print(f"No Sentinel-2 images found for date range: {start_date} to {end_date}")
            return None

        # Sort the collection by cloud cover and get the least cloudy image
        image = ee.Image(filtered_collection.sort('CLOUDY_PIXEL_PERCENTAGE').first())
        
        # Check if the image has bands
        band_names = image.bandNames().getInfo()
        if not band_names:
            print(f"Retrieved Sentinel-2 image has no bands for date range: {start_date} to {end_date}")
            return None

        image_date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        print(f"Retrieved Sentinel-2 image date: {image_date}")
        print(f"Retrieved Sentinel-2 image bands: {band_names}")
        return image
    except Exception as e:
        print(f"Error retrieving Sentinel-2 image: {str(e)}")
        return None
