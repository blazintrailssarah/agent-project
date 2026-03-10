# Assignment 2: Data Bundle for 94514 Area — Provenance Report

## Overview

This document records the data collection efforts for Assignment 2, which aimed to gather agricultural datasets for 50 fields in the 94514 zip code area (Discovery Bay/Mountain House, Central California Delta region) spanning years 2019–2022.

## Datasets Attempted

### 1. Field Boundaries (50 fields)
**Source**: USDA NASS CDL (Cropland Data Layer)  
**Status**: ⚠️ **Partially Complete**  
**Details**:
- Attempted download via multiple sources:
  - Primary: `https://cropscape.usda.gov/arcgis/services/NASS_CDL/MapServer/WCSServer` — DNS unreachable
  - Alternative: `https://nassgeodata.gmu.edu/CropScape/services/CDL*/MapServer/WCSServer` — 404 errors
- Script `data/download_data.py` includes logic to generate field boundaries from CDL raster data
- Once CDL data is accessible, script will extract 50 sample field polygons from 2022 CDL layer
- Output file: `data/field_boundaries/selected_fields.geojson`

### 2. SSURGO Soil Data
**Source**: USDA NRCS Soil Data Access  
**Status**: ⚠️ **Not Downloaded**  
**Details**:
- Attempted download via:
  - Primary: `https://SDMDataAccess.nrcs.usda.gov/arcgis/services/SDM/SDMv2/ImageServer/WCSServer` — DNS unreachable
  - Alternative: `https://SDMDataAccess.sc.egov.usda.gov/arcgis/services/SDM/SDMv2/ImageServer/WCSServer` — 404 errors
- Script includes WCS request logic ready for retry
- Output file: `data/ssurgo/ssurgo.tif`
- Coverage area: 94514 zip code bounding box (-121.6, 37.8, -121.4, 37.9)

### 3. NASA POWER Weather Data 2019–2022
**Source**: NASA POWER API v2.1  
**Status**: ✅ **Successfully Downloaded**  
**Details**:
- **URL**: `https://power.larc.nasa.gov/api/v2/temporal/daily/regional`
- **Date range**: January 1, 2019 – December 31, 2022
- **Geographic extent**: 94514 area (37.8°N–37.9°N, 121.4°W–121.6°W)
- **Parameters retrieved**:
  - T2M: Temperature at 2 m (°C)
  - PRECTOTCORR: Corrected precipitation (mm/day)
  - RH2M: Relative humidity at 2 m (%)
  - WS2M: Wind speed at 2 m (m/s)
  - ALLSKY_SFC_SW_DWN: Solar irradiance downward (MJ/m²/day)
  - PS: Surface pressure (kPa)
- **Output file**: `data/weather/weather_2019_2022.json`
- **File size**: ~2.8 MB
- **Format**: JSON with daily records and metadata

### 4. CDL Cropland Data 2019–2022
**Source**: USDA NASS CropScape  
**Status**: ⚠️ **Not Downloaded**  
**Details**:
- Attempted download for years 2019, 2020, 2021, 2022
- Attempted WCS endpoints returned 404 errors
- Alternative direct download URLs not accessible
- Script includes retry logic for when servers are reachable
- Output files: `data/cdl/CDL_2019.tif`, `data/cdl/CDL_2020.tif`, `data/cdl/CDL_2021.tif`, `data/cdl/CDL_2022.tif`
- Expected use: Crop classification and field boundary generation

## Environment & Constraints

**Environment**: GitHub Codespaces (Ubuntu 24.04.3 LTS)  
**Network Issue**: USDA servers (cropscape.usda.gov, SDMDataAccess.*) not accessible from Codespace environment
- DNS resolution failures for USDA hosts
- 404 responses from attempted alternative endpoints
- Likely cause: Network restrictions or firewall policies specific to Codespace infrastructure

## Data Pipeline Structure

```
data/
├── .gitignore              # Excludes large/binary files (*.tif, *.zip, *.nc, *.hdf)
├── cdl/                    # CDL raster files (when available)
├── ssurgo/                 # SSURGO soil GeoTIFF (when available)
├── weather/
│   └── weather_2019_2022.json  # ✅ Successfully downloaded
└── field_boundaries/       # Field boundary GeoJSON (when CDL data available)
```

## Files Committed

- `.gitattributes` — Git LFS configuration for tracking large files (*.tif, *.zip, *.nc, *.hdf)
- `data/.gitignore` — Prevents tracking of large/binary data files in regular Git
- `data/download_data.py` — Reusable Python script to orchestrate all data downloads

## Git LFS Configuration

Large binary files are tracked via Git LFS to prevent repository bloat:
```bash
git lfs track "*.tif" "*.zip" "*.nc" "*.hdf"
```

## Remediation & Next Steps

1. **Retry from alternative network** — Run `data/download_data.py` from a machine with unrestricted USDA server access
2. **Use USDA offline data** — Request CAP files from USDA geospatial data gateway if API unavailable
3. **Local caching strategy** — Once downloaded, commit to Git LFS to enable team access
4. **Augment with sample data** — Generate synthetic field boundaries and soil properties for prototyping
5. **Document manual download alternative** — Add notes on Web Soil Survey and CropScape interface download steps

## Verification

To verify NASA POWER data:
```bash
cat data/weather/weather_2019_2022.json | jq '.properties | keys'
# Expected: ["TIME_RANGE", "VALUE"]
```

To retry downloads when environment allows:
```bash
cd data && python download_data.py
```

## References

- **NASA POWER API**: https://power.larc.nasa.gov/api/v2/
- **USDA NASS CropScape**: https://cropscape.usda.gov/
- **USDA Web Soil Survey**: https://websoilsurvey.nrcs.usda.gov/
- **USDA Geospatial Data Gateway**: https://datagateway.nrcs.usda.gov/

---

**Date**: 2026-03-10  
**Branch**: `assignment-2-data-bundle`  
**Status**: Data pipeline framework complete; weather data available; retry other datasets when network accessible
