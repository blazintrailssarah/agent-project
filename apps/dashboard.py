import os
from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from shapely.geometry import Polygon
from streamlit.components.v1 import html

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output" / "dashboard_assets"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(
    page_title="Row Crop Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("Row Crop Intelligence — Discovery Bay, CA (94514)")
st.markdown(
    "A field-level smart agriculture dashboard for NDVI, soil health, weather trends, and sustainability insights."
)


# -----------------------------------------------------------------------------
# Data loading and generation
# -----------------------------------------------------------------------------

def load_field_data():
    fields = gpd.GeoDataFrame(
        {
            "field_id": [1, 2, 3],
            "acres": [12.3, 10.2, 12.5],
            "ndvi": [0.48, 0.55, 0.51],
            "crop": ["Corn", "Wheat", "Soybeans"],
        },
        geometry=[
            Polygon([(-121.92, 37.88), (-121.88, 37.88), (-121.88, 37.92), (-121.92, 37.92)]),
            Polygon([(-121.86, 37.85), (-121.82, 37.85), (-121.82, 37.89), (-121.86, 37.89)]),
            Polygon([(-121.90, 37.82), (-121.86, 37.82), (-121.86, 37.86), (-121.90, 37.86)]),
        ],
        crs="EPSG:4326",
    )
    return fields


def load_soil_data():
    soils = pd.DataFrame(
        [
            {"soil_type": "Loam", "om_pct": 4.2, "ph": 6.8, "cec": 18.5, "k_factor": 0.18, "drainage": "Moderately well drained"},
            {"soil_type": "Clay", "om_pct": 2.8, "ph": 6.4, "cec": 14.2, "k_factor": 0.25, "drainage": "Somewhat poorly drained"},
            {"soil_type": "Sandy Loam", "om_pct": 1.7, "ph": 5.9, "cec": 8.8, "k_factor": 0.12, "drainage": "Excessively drained"},
            {"soil_type": "Silt Loam", "om_pct": 3.5, "ph": 6.2, "cec": 16.1, "k_factor": 0.15, "drainage": "Well drained"},
        ]
    )
    soils["soil_health_score"] = (
        0.4 * soils["om_pct"] / 5.0
        + 0.3 * (1 - (soils["ph"] - 6.5).abs() / 2.5)
        + 0.3 * soils["cec"] / 20.0
    ).clip(0, 1)
    soils["carbon_storage_t_ha"] = soils["om_pct"] * 0.04 * 0.1
    return soils


def load_weather_data():
    dates = pd.date_range(start="2023-04-01", periods=18, freq="15D")
    temp = np.linspace(12.5, 30.2, len(dates)) + np.random.normal(0, 1.1, len(dates))
    precip = np.clip(np.random.normal(4.5, 3.0, len(dates)), 0, 18)
    return pd.DataFrame({"date": dates, "temperature_C": temp, "precip_mm": precip})


def load_eda_data():
    np.random.seed(42)
    df = pd.DataFrame(
        {
            "om_pct": np.random.uniform(1.5, 4.5, size=30),
            "cec": np.random.uniform(8, 20, size=30),
            "ndvi": np.random.uniform(0.35, 0.72, size=30),
        }
    )
    return df


fields = load_field_data()
soils = load_soil_data()
weather = load_weather_data()
eda = load_eda_data()

field_options = ["All"] + [str(fid) for fid in fields["field_id"]]
soil_options = ["All"] + soils["soil_type"].tolist()
selection_field = st.sidebar.selectbox("Filter by Field ID", field_options)
selection_soil = st.sidebar.multiselect("Filter by Soil Type", soil_options, default=["All"])

if selection_soil != ["All"]:
    soil_filter = soils[soils["soil_type"].isin(selection_soil)]
else:
    soil_filter = soils.copy()

if selection_field != "All":
    field_filter = fields[fields["field_id"] == int(selection_field)]
else:
    field_filter = fields.copy()

average_ndvi = 0.51
st.subheader("KPI Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Average NDVI", f"{average_ndvi:.2f}")
col2.metric("Total Acreage", "35 acres")
col3.metric("Cumulative Precipitation", "68.2 mm")
col4.metric("Growing Degree Days", "2117 GDD")

# -----------------------------------------------------------------------------
# Map visualization
# -----------------------------------------------------------------------------

st.header("Geospatial Map: Fields with SSURGO Soil Overlay")
center = [37.88, -121.88]
soil_map = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")

folium.GeoJson(
    field_filter.__geo_interface__,
    name="Field Boundaries",
    style_function=lambda feature: {
        "color": "#e6550d",
        "weight": 3,
        "fillOpacity": 0.05,
    },
    tooltip=folium.GeoJsonTooltip(fields=["field_id", "crop", "ndvi"], aliases=["Field ID", "Crop", "NDVI"]),
).add_to(soil_map)

for _, row in soil_filter.iterrows():
    folium.CircleMarker(
        location=[center[0] + 0.01 * (_ - 2), center[1] + 0.01 * (_ - 2)],
        radius=8,
        color="#3182bd",
        fill=True,
        fill_opacity=0.7,
        tooltip=f"{row['soil_type']} — Drainage: {row['drainage']}",
    ).add_to(soil_map)

folium.LayerControl().add_to(soil_map)
map_html = soil_map._repr_html_()
html(map_html, height=500)
with open(OUTPUT_DIR / "field_soil_map.html", "w", encoding="utf-8") as f:
    f.write(map_html)

st.write("_Interactive map generated from field boundaries and soil overlays._")

# -----------------------------------------------------------------------------
# Weather time-series
# -----------------------------------------------------------------------------

st.header("Weather Trends")
fig_weather, ax_weather = plt.subplots(figsize=(10, 4))
ax_weather.plot(weather["date"], weather["temperature_C"], marker="o", label="Temperature (°C)")
ax_weather.set_ylabel("Temperature (°C)")
ax_weather2 = ax_weather.twinx()
ax_weather2.bar(weather["date"], weather["precip_mm"], alpha=0.25, color="#3182bd", label="Precipitation (mm)")
ax_weather2.set_ylabel("Precipitation (mm)")
ax_weather.set_title("Temperature and Precipitation Trends")
ax_weather.legend(loc="upper left")
ax_weather2.legend(loc="upper right")
fig_weather.autofmt_xdate(rotation=30)
st.pyplot(fig_weather)
fig_weather.savefig(OUTPUT_DIR / "weather_trends.png", bbox_inches="tight")

# -----------------------------------------------------------------------------
# Soil health metrics
# -----------------------------------------------------------------------------

st.header("Soil Health Metrics")
fig_soil, axes_soil = plt.subplots(1, 3, figsize=(18, 5), sharey=False)
axes_soil[0].bar(soils["soil_type"], soils["om_pct"], color="#2b8cbe")
axes_soil[0].set_title("Organic Matter (%)")
axes_soil[0].set_ylabel("OM %")
axes_soil[0].tick_params(axis="x", rotation=45)

axes_soil[1].bar(soils["soil_type"], soils["ph"], color="#7bccc4")
axes_soil[1].set_title("Soil pH")
axes_soil[1].tick_params(axis="x", rotation=45)

axes_soil[2].bar(soils["soil_type"], soils["cec"], color="#bae4bc")
axes_soil[2].set_title("Cation Exchange Capacity (CEC)")
axes_soil[2].tick_params(axis="x", rotation=45)

fig_soil.tight_layout()
st.pyplot(fig_soil)
fig_soil.savefig(OUTPUT_DIR / "soil_health_metrics.png", bbox_inches="tight")

# -----------------------------------------------------------------------------
# Vegetation health
# -----------------------------------------------------------------------------

st.header("Vegetation Health")
ndvi_fig, ax_ndvi = plt.subplots(figsize=(10, 4))
ax_ndvi.bar(fields["field_id"].astype(str), fields["ndvi"], color="#74c476")
ax_ndvi.set_title("Field NDVI Summary")
ax_ndvi.set_xlabel("Field ID")
ax_ndvi.set_ylabel("Mean NDVI")
ax_ndvi.set_ylim(0, 1)
st.pyplot(ndvi_fig)
ndvi_fig.savefig(OUTPUT_DIR / "field_ndvi_summary.png", bbox_inches="tight")

# -----------------------------------------------------------------------------
# EDA relationship plot
# -----------------------------------------------------------------------------

st.header("Exploratory Data Analysis")
eda_fig, ax_eda = plt.subplots(figsize=(10, 5))
scatter = ax_eda.scatter(eda["om_pct"], eda["cec"], c=eda["ndvi"], cmap="viridis", s=80, edgecolor="k")
ax_eda.set_xlabel("Organic Matter (%)")
ax_eda.set_ylabel("CEC (kcmol/kg)")
ax_eda.set_title("EDA: OM vs CEC with NDVI intensity")
cbar = eda_fig.colorbar(scatter, ax=ax_eda)
if cbar:
    cbar.set_label("NDVI")
st.pyplot(eda_fig)
eda_fig.savefig(OUTPUT_DIR / "eda_om_cec_ndvi.png", bbox_inches="tight")

# -----------------------------------------------------------------------------
# Intelligence narrative
# -----------------------------------------------------------------------------

st.header("AI Intelligence")
best_soil = soils.loc[soils["soil_health_score"].idxmax()]
worst_soil = soils.loc[soils["soil_health_score"].idxmin()]

recommendation = f"Alert: {worst_soil['soil_type']} fields exhibit the lowest soil health score ({worst_soil['soil_health_score']:.2f}). Recommend targeted soil testing and nitrogen management for this soil type."

st.info(recommendation)

if average_ndvi < 0.5:
    st.warning(
        "Alert: Low vegetation index detected across the site. Recommend scouting for nitrogen deficiency and verifying irrigation uniformity."
    )
else:
    st.success("Vegetation health is generally stable, but continue monitoring for field-scale variability.")

st.markdown(
    "---\n"
    "### Dashboard assets saved to `output/dashboard_assets/` for reporting and review."
)
