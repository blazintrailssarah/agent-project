import requests
import geopandas as gpd
from owslib.wcs import WebCoverageService
import os
import rasterio
from rasterio.features import shapes
from shapely.geometry import box

# Create directories (already done, but ensure)
os.makedirs('data/cdl', exist_ok=True)
os.makedirs('data/ssurgo', exist_ok=True)
os.makedirs('data/weather', exist_ok=True)
os.makedirs('data/field_boundaries', exist_ok=True)

# Download CDL for 2019-2022 using alternative WCS
years = [2019, 2020, 2021, 2022]
bbox = (-121.6, 37.8, -121.4, 37.9)
for year in years:
    print(f'Downloading CDL for {year}...')
    try:
        # Try alternative WCS URL
        wcs_url = f'https://nassgeodata.gmu.edu/CropScape/services/CDL{year}_06/MapServer/WCSServer'
        wcs = WebCoverageService(url=wcs_url, version='2.0.1')
        response = wcs.getCoverage(identifier=f'CDL{year}_06:CDL', bbox=bbox, format='GeoTIFF')
        with open(f'data/cdl/CDL_{year}.tif', 'wb') as f:
            f.write(response.read())
        print(f'CDL {year} downloaded.')
    except Exception as e:
        print(f'Failed to download CDL {year}: {e}')

# Use CDL 2022 for field boundaries if available
print('Generating field boundaries from CDL 2022...')
try:
    with rasterio.open('data/cdl/CDL_2022.tif') as src:
        image = src.read(1)
        transform = src.transform
        shapes_list = list(shapes(image, transform=transform))
        polygons = [{'geometry': geom, 'properties': {'value': value}} for geom, value in shapes_list if value > 0]
    gdf = gpd.GeoDataFrame.from_features(polygons, crs=src.crs)
    # Clip to bbox if needed
    bbox_geom = box(*bbox)
    gdf = gdf[gdf.geometry.intersects(bbox_geom)]
    selected = gdf.sample(min(50, len(gdf)))
    selected.to_file('data/field_boundaries/selected_fields.geojson', driver='GeoJSON')
    print(f'Selected {len(selected)} fields.')
except Exception as e:
    print(f'Failed to generate field boundaries: {e}')

# Download SSURGO soil data using alternative URL
print('Downloading SSURGO data...')
try:
    # Try alternative SSURGO WCS URL
    wcs = WebCoverageService(url='https://SDMDataAccess.sc.egov.usda.gov/arcgis/services/SDM/SDMv2/ImageServer/WCSServer', version='2.0.1')
    response = wcs.getCoverage(identifier='SDM:SSURGO_Map_Units', bbox=bbox, format='GeoTIFF')
    with open('data/ssurgo/ssurgo.tif', 'wb') as f:
        f.write(response.read())
    print('SSURGO data downloaded.')
except Exception as e:
    print(f'Failed to download SSURGO: {e}')

# Download NASA POWER weather data
print('Downloading weather data...')
try:
    url = 'https://power.larc.nasa.gov/api/v2/temporal/daily/regional'
    params = {
        'parameters': 'T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PS',
        'community': 'ag',
        'start': '20190101',
        'end': '20221231',
        'north': 37.9,
        'south': 37.8,
        'west': -121.6,
        'east': -121.4,
        'format': 'json'
    }
    response = requests.get(url, params=params)
    with open('data/weather/weather_2019_2022.json', 'w') as f:
        f.write(response.text)
    print('Weather data downloaded.')
except Exception as e:
    print(f'Failed to download weather data: {e}')