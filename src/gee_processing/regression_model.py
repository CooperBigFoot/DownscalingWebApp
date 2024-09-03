import ee
from typing import List, Dict


def create_ridge_regression_model(
    landsat_image: ee.Image,
    dependent_var: str,
    independent_vars: List[str],
    region: ee.Geometry,
    scale: float = 30,
    lambda_: float = 0.1,
    num_samples: int = 5000,
) -> Dict[str, ee.Number]:
    """
    Creates a ridge regression model using Landsat data.

    Args:
        landsat_image (ee.Image): Input Landsat image with LST and spectral indices.
        dependent_var (str): Name of the dependent variable band (e.g., 'LST').
        independent_vars (List[str]): List of independent variable band names (e.g., ['NDVI', 'NDBI', 'NDWI']).
        region (ee.Geometry): Region of interest for sampling points.
        scale (float): Scale in meters for sampling points. Default is 30 (Landsat resolution).
        lambda_ (float): Ridge regression regularization parameter. Default is 0.1.
        num_samples (int): Number of random points to sample. Default is 5000.

    Returns:
        Dict[str, ee.Number]: Dictionary containing regression coefficients and intercept.
    """
    # Create an image with the independent and dependent variables
    regression_image = landsat_image.select(independent_vars + [dependent_var])

    # Sample the image
    samples = regression_image.sample(region=region, scale=scale, numPixels=num_samples)

    # Perform ridge regression
    regression = samples.reduceColumns(
        **{
            "reducer": ee.Reducer.ridgeRegression(
                **{"numX": len(independent_vars), "numY": 1, "lambda": lambda_}
            ),
            "selectors": independent_vars + [dependent_var],
        }
    )

    # Extract coefficients and intercept
    coefficients = ee.Array(regression.get("coefficients")).toList()

    # Create a dictionary with named coefficients
    coeff_dict = {var: coefficients.get(i) for i, var in enumerate(independent_vars)}
    coeff_dict["intercept"] = coefficients.get(
        -1
    )  # The last coefficient is the intercept

    return coeff_dict


def apply_regression_model(
    image: ee.Image, coefficients: Dict[str, ee.Number], independent_vars: List[str]
) -> ee.Image:
    """
    Applies the ridge regression model to an image.

    Args:
        image (ee.Image): Input image with spectral indices.
        coefficients (Dict[str, ee.Number]): Regression coefficients and intercept.
        independent_vars (List[str]): List of independent variable band names.

    Returns:
        ee.Image: Image with predicted LST band added.
    """
    # Create an image of the intercept
    prediction = ee.Image.constant(coefficients["intercept"])

    # Add the weighted independent variables
    for var in independent_vars:
        prediction = prediction.add(image.select(var).multiply(coefficients[var]))

    return image.addBands(prediction.rename("LST_predicted"))


def calculate_residuals(image: ee.Image) -> ee.Image:
    """
    Calculates residuals between observed and predicted LST.

    Args:
        image (ee.Image): Input image with observed LST and predicted LST bands.

    Returns:
        ee.Image: Image with residuals band added.
    """
    residuals = (
        image.select("LST")
        .subtract(image.select("LST_predicted"))
        .rename("LST_residuals")
    )
    return image.addBands(residuals)
