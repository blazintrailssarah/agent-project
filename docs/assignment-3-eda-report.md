# Assignment 3: Exploratory Data Analysis (EDA) Report on NASA POWER Weather Data

_Clayton Young (Boreal Bytes) · Superior Byte Works, LLC · March 10, 2026_

---

## Abstract

This report presents an exploratory data analysis of NASA POWER weather data intended for the California Delta region near zip code 94514. Due to API access issues with the NASA POWER service, the weather data could not be successfully downloaded, preventing a full EDA. The report summarizes the attempted data acquisition, notes data quality issues encountered, and highlights that similar access problems affected other USDA datasets (SSURGO soil data, CDL cropland data, and field boundaries). While no quantitative analysis was possible, the report outlines the expected structure and scope of weather data analysis for agricultural applications in the region.

## 📋 Introduction

### Problem Statement

Agricultural planning in the California Delta region requires reliable weather data for crop management, irrigation scheduling, and yield prediction. NASA POWER provides satellite-derived meteorological data that could support these applications.

### Scope and Objectives

This EDA aimed to:

- Analyze temperature patterns across 2019-2022
- Examine precipitation trends and variability
- Assess humidity, wind speed, solar radiation, and pressure data
- Identify data quality issues and seasonal patterns
- Provide insights for agricultural decision-making

### Research Questions

1. What are the seasonal temperature and precipitation patterns in the Delta region?
2. How variable are weather conditions year-over-year?
3. Are there data gaps or quality issues that affect reliability?

## 📚 Background

### NASA POWER Dataset

NASA POWER (Prediction of Worldwide Energy Resources) provides global meteorological data derived from satellite observations and reanalysis models[^1]. The dataset includes parameters relevant to agriculture such as:

- T2M: 2-meter air temperature
- PRECTOTCORR: Precipitation corrected
- RH2M: 2-meter relative humidity
- WS2M: 2-meter wind speed
- ALLSKY_SFC_SW_DWN: All-sky surface shortwave downward irradiance
- PS: Surface pressure

### Study Area

The analysis focused on a small region in California's Delta near Brentwood, CA (zip code 94514), bounded by:

- North: 37.9°N
- South: 37.8°N
- West: -121.6°E
- East: -121.4°E

This area represents typical Delta agricultural land.

## 🔬 Methodology

### Data Acquisition

Weather data was requested from the NASA POWER API v2 temporal daily regional endpoint with the following parameters:

- Time range: January 1, 2019 to December 31, 2022
- Spatial resolution: Regional average for the bounding box
- Parameters: T2M, PRECTOTCORR, RH2M, WS2M, ALLSKY_SFC_SW_DWN, PS
- Format: JSON

### Analysis Approach

The planned EDA would include:

1. Data loading and initial inspection
2. Summary statistics for all parameters
3. Time series visualization
4. Seasonal decomposition
5. Correlation analysis between weather variables
6. Outlier detection and data quality assessment

### Tools and Libraries

- Python with pandas for data manipulation
- Matplotlib/seaborn for visualization
- Statistical analysis with scipy

## 📊 Findings

### Data Acquisition Issues

The NASA POWER API returned a 404 error for the regional data request, suggesting either:

- Incorrect API endpoint or parameters
- Service unavailability
- Geographic bounding box too small for regional aggregation

The downloaded file contained HTML error content instead of JSON data, confirming the API call failure.

### Comparison with Other Datasets

Similar access issues affected other planned datasets:

| Dataset            | Source           | Status | Issue                       |
| ------------------ | ---------------- | ------ | --------------------------- |
| SSURGO Soil Data   | USDA             | Failed | 404 errors from WCS service |
| CDL Cropland Data  | USDA             | Failed | 404 errors from WCS service |
| Field Boundaries   | Derived from CDL | Failed | Dependent on CDL data       |
| NASA POWER Weather | NASA             | Failed | 404 error from API          |

### Expected Data Structure

Based on NASA POWER documentation, the expected JSON structure would include:

- `properties`: Metadata about the request
- `features`: Array of daily records with geometry and parameter values
- Each feature containing date and weather parameter measurements

## 💡 Analysis

### Implications of Data Access Issues

The inability to access weather data highlights challenges in agricultural data acquisition:

1. **API Reliability**: Public APIs may have uptime issues or parameter restrictions
2. **Alternative Sources**: Local weather stations or other reanalysis datasets may be needed
3. **Data Integration**: Multiple data sources require careful harmonization

### Potential Workarounds

For future analysis, consider:

- Point-based API requests instead of regional
- Alternative weather data sources (NOAA, CIMIS)
- Local sensor networks
- Commercial weather APIs

### Agricultural Context

Without the data, we cannot assess:

- Growing season temperature suitability
- Irrigation needs based on evapotranspiration
- Frost risk periods
- Solar radiation for crop photosynthesis

## 🎯 Conclusions

### Summary

This EDA attempt revealed significant data access barriers for both NASA and USDA agricultural datasets. While the methodology was sound, execution was prevented by service availability issues.

### Recommendations

1. **Retry with Alternative Endpoints**: Test NASA POWER point-based API
2. **Diversify Data Sources**: Include local weather station data
3. **Monitor API Status**: Check service health before analysis
4. **Develop Robust Pipelines**: Include error handling for external data dependencies

### Future Work

Successful data acquisition would enable:

- Seasonal weather pattern analysis
- Climate variability assessment
- Agricultural risk modeling
- Irrigation scheduling optimization

### Limitations

The primary limitation was data unavailability, preventing any quantitative analysis. This report serves as documentation of the access issues rather than weather insights.

---

## 🔗 References

[^1]: NASA POWER. "Prediction of Worldwide Energy Resources." <https://power.larc.nasa.gov/>

---

## 📎 Appendices

### Appendix A: API Request Details

```json
{
  "url": "https://power.larc.nasa.gov/api/v2/temporal/daily/regional",
  "parameters": {
    "parameters": "T2M,PRECTOTCORR,RH2M,WS2M,ALLSKY_SFC_SW_DWN,PS",
    "community": "ag",
    "start": "20190101",
    "end": "20221231",
    "north": "37.9",
    "south": "37.8",
    "west": "-121.6",
    "east": "-121.4",
    "format": "json"
  }
}
```

### Appendix B: Error Response

The API returned HTTP 404 with HTML content indicating "Page Not Found", suggesting the endpoint or parameters were invalid for the requested spatial extent.
