import ee
from typing import Union, List, Dict, Any
import datetime


def export_image_to_asset(
    image: ee.Image,
    description: str,
    asset_id: str,
    scale: int = 30,
    crs: str = "EPSG:4326",
    region: ee.Geometry = None,
    max_pixels: int = 1e13,
) -> ee.batch.Task:
    """
    Exports an Earth Engine image to an asset.

    Args:
        image (ee.Image): The image to export.
        description (str): Description of the export task.
        asset_id (str): The destination asset ID.
        scale (int, optional): The resolution in meters per pixel. Defaults to 30.
        crs (str, optional): The coordinate reference system. Defaults to "EPSG:4326".
        region (ee.Geometry, optional): The region to export. Defaults to the image's geometry.
        max_pixels (int, optional): The maximum number of pixels to export. Defaults to 1e13.

    Returns:
        ee.batch.Task: The export task.
    """
    if region is None:
        region = image.geometry()

    task = ee.batch.Export.image.toAsset(
        image=image,
        description=description,
        assetId=asset_id,
        scale=scale,
        crs=crs,
        region=region,
        maxPixels=max_pixels,
    )
    task.start()
    return task


def export_image_to_drive(
    image: ee.Image,
    description: str,
    folder: str,
    file_name: str,
    scale: int = 30,
    crs: str = "EPSG:4326",
    region: ee.Geometry = None,
    max_pixels: int = 1e13,
    file_format: str = "GeoTIFF",
) -> ee.batch.Task:
    """
    Exports an Earth Engine image to Google Drive.

    Args:
        image (ee.Image): The image to export.
        description (str): Description of the export task.
        folder (str): The destination folder in Google Drive.
        file_name (str): The name of the file to be created.
        scale (int, optional): The resolution in meters per pixel. Defaults to 30.
        crs (str, optional): The coordinate reference system. Defaults to "EPSG:4326".
        region (ee.Geometry, optional): The region to export. Defaults to the image's geometry.
        max_pixels (int, optional): The maximum number of pixels to export. Defaults to 1e13.
        file_format (str, optional): The output file format. Defaults to "GeoTIFF".

    Returns:
        ee.batch.Task: The export task.
    """
    if region is None:
        region = image.geometry()

    task = ee.batch.Export.image.toDrive(
        image=image,
        description=description,
        folder=folder,
        fileNamePrefix=file_name,
        scale=scale,
        crs=crs,
        region=region,
        maxPixels=max_pixels,
        fileFormat=file_format,
    )
    task.start()
    return task


def date_to_ee_date(date: Union[str, datetime.date, datetime.datetime]) -> ee.Date:
    """
    Converts a Python date or datetime object, or a date string, to an ee.Date object.

    Args:
        date (Union[str, datetime.date, datetime.datetime]): The date to convert.

    Returns:
        ee.Date: The converted Earth Engine date.
    """
    if isinstance(date, str):
        return ee.Date(date)
    elif isinstance(date, (datetime.date, datetime.datetime)):
        return ee.Date(date.isoformat())
    else:
        raise ValueError("Invalid date format. Use a string, date, or datetime object.")


def add_timestamp_band(image: ee.Image) -> ee.Image:
    """
    Adds a timestamp band to an image.

    Args:
        image (ee.Image): The input image.

    Returns:
        ee.Image: The image with an added timestamp band.
    """
    return image.addBands(ee.Image(image.date().millis()).rename("timestamp").toLong())


def replace_masked_values(
    image: ee.Image, value: Union[int, float] = 0, mask_band: str = None
) -> ee.Image:
    """
    Replaces masked values in an image with a specified value.

    Args:
        image (ee.Image): The input image.
        value (Union[int, float], optional): The value to replace masked pixels with. Defaults to 0.
        mask_band (str, optional): The name of the band to use as a mask. If None, uses the image mask.

    Returns:
        ee.Image: The image with masked values replaced.
    """
    if mask_band is not None:
        mask = image.select(mask_band).mask()
    else:
        mask = image.mask()

    return image.unmask(value).updateMask(mask.Not().Not())


def clip_to_region(
    image_or_collection: Union[ee.Image, ee.ImageCollection], region: ee.Geometry
) -> Union[ee.Image, ee.ImageCollection]:
    """
    Clips an image or image collection to a specified region.

    Args:
        image_or_collection (Union[ee.Image, ee.ImageCollection]): The input image or image collection.
        region (ee.Geometry): The region to clip to.

    Returns:
        Union[ee.Image, ee.ImageCollection]: The clipped image or image collection.
    """
    if isinstance(image_or_collection, ee.Image):
        return image_or_collection.clip(region)
    elif isinstance(image_or_collection, ee.ImageCollection):
        return image_or_collection.map(lambda img: img.clip(region))
    else:
        raise ValueError("Input must be an ee.Image or ee.ImageCollection")


def get_image_stats(
    image: ee.Image, region: ee.Geometry, scale: int = 30, max_pixels: int = 1e9
) -> Dict[str, Any]:
    """
    Calculates basic statistics for all bands of an image within a region.

    Args:
        image (ee.Image): The input image.
        region (ee.Geometry): The region to calculate statistics for.
        scale (int, optional): The scale in meters of the projection to work in. Defaults to 30.
        max_pixels (int, optional): The maximum number of pixels to reduce. Defaults to 1e9.

    Returns:
        Dict[str, Any]: A dictionary containing the statistics for each band.
    """
    stats = image.reduceRegion(
        reducer=ee.Reducer.mean()
        .combine(reducer2=ee.Reducer.stdDev(), sharedInputs=True)
        .combine(reducer2=ee.Reducer.minMax(), sharedInputs=True),
        geometry=region,
        scale=scale,
        maxPixels=max_pixels,
    )
    return stats.getInfo()


def create_ee_polygon_from_bounds(
    min_lon: float, min_lat: float, max_lon: float, max_lat: float
) -> ee.Geometry.Polygon:
    """
    Creates an Earth Engine Polygon from bounding coordinates.

    Args:
        min_lon (float): Minimum longitude.
        min_lat (float): Minimum latitude.
        max_lon (float): Maximum longitude.
        max_lat (float): Maximum latitude.

    Returns:
        ee.Geometry.Polygon: An Earth Engine Polygon object.
    """
    return ee.Geometry.Polygon(
        [
            [min_lon, min_lat],
            [min_lon, max_lat],
            [max_lon, max_lat],
            [max_lon, min_lat],
            [min_lon, min_lat],
        ]
    )


def apply_scale_factors(image: ee.Image) -> ee.Image:
    """
    Applies scale factors to Landsat 8/9 Collection 2 images.

    Args:
        image (ee.Image): Input Landsat 8/9 image.

    Returns:
        ee.Image: Landsat image with scale factors applied.
    """
    optical_bands = image.select("SR_B.").multiply(0.0000275).add(-0.2)
    thermal_bands = (
        image.select("ST_B.*").multiply(0.00341802).add(149.0).subtract(273.15)
    )
    return image.addBands(optical_bands, None, True).addBands(thermal_bands, None, True)
