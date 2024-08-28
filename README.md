# Land Surface Temperature Downscaling

This project implements a Streamlit web application for downscaling Land Surface Temperature (LST) data using Landsat 8/9 and Sentinel-2 imagery. It's based on the methodology described in the following paper:

Onačillová, K.; Gallay, M.; Paluba, D.; Péliová, A.; Tokarčík, O.; Laubertová, D. Combining Landsat 8 and Sentinel-2 Data in Google Earth Engine to Derive Higher Resolution Land Surface Temperature Maps in Urban Environment. Remote Sens. 2022, 14, 4076.

[https://doi.org/10.3390/rs14164076](https://doi.org/10.3390/rs14164076)

## Features

- Selection of Landsat 8 or Landsat 9 imagery
- Date range selection for image acquisition
- Cloud cover filtering
- Generation of Landsat and Sentinel-2 image collections
- LST downscaling from 30m (Landsat) to 10m (Sentinel-2) resolution
- Interactive map display of results
- Spectral indices vs LST charts

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/lst-downscaling.git
   cd lst-downscaling
   ```

2. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Set up Google Earth Engine authentication:
   - If you haven't already, sign up for Google Earth Engine at https://earthengine.google.com/signup/
   - Follow the instructions to authenticate your Earth Engine account

## Usage

1. Run the Streamlit app:
   ```
   streamlit run src/app.py
   ```

2. Open your web browser and go to the URL displayed in the terminal (usually http://localhost:8501)

3. Use the sidebar to set parameters:
   - Select the date range
   - Choose the Landsat collection (8 or 9)
   - Set the maximum cloud cover percentage
   - Click "Generate Landsat and Sentinel-2 Image Collections"

4. Once the collections are generated, select the specific Landsat and Sentinel-2 images you want to use

5. Click "Generate Downscaled LST" to perform the downscaling

6. Use the layer selection to choose which layers to display on the map

7. Optionally, generate charts of spectral indices vs Landsat LST

## Project Structure

```
.
├── README.md
└── src
├── init.py
├── app.py
├── gee_processing
│   ├── init.py
│   ├── image_collection.py
│   ├── lst_downscaling.py
│   ├── utils.py
│   └── visualization.py
└── ui
├── init.py
├── charts.py
├── map_display.py
└── sidebar.py
```

## Contributing

Contributions to this project are welcome. Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The authors of the original paper for their methodology
- The Google Earth Engine team for providing the platform and Python API
- The Streamlit team for their excellent web app framework