import ee
from typing import List, Dict
from .regression_model import apply_regression_model, calculate_residuals


def downscale_lst(
    sentinel_image: ee.Image,
    landsat_image: ee.Image,
    regression_coefficients: Dict[str, ee.Number],
    independent_vars: List[str],
) -> ee.Image:
    """
    Downscales Landsat LST using Sentinel-2 data and the ridge regression model.

    Args:
        sentinel_image (ee.Image): Sentinel-2 image with spectral indices.
        landsat_image (ee.Image): Landsat image with LST and spectral indices.
        regression_coefficients (Dict[str, ee.Number]): Ridge regression coefficients and intercept.
        independent_vars (List[str]): List of independent variable band names.

    Returns:
        ee.Image: Downscaled LST image at Sentinel-2 resolution.
    """
    # Apply regression model to Sentinel-2 image
    sentinel_predicted_lst = apply_regression_model(
        sentinel_image, regression_coefficients, independent_vars
    )

    # Calculate residuals from Landsat
    landsat_residuals = calculate_residuals(
        apply_regression_model(landsat_image, regression_coefficients, independent_vars)
    )

    # Resample Landsat residuals to Sentinel-2 resolution
    resampled_residuals = (
        landsat_residuals.select("LST_residuals")
        .resample("bilinear")
        .reproject(crs=sentinel_image.projection(), scale=10)
    )

    # Add resampled residuals to Sentinel-2 predicted LST
    downscaled_lst = (
        sentinel_predicted_lst.select("LST_predicted")
        .add(resampled_residuals)
        .rename("LST_downscaled")
    )

    return sentinel_image.addBands(downscaled_lst)
