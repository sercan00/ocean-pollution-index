# Project Files & Data Guide

This document explains what every file in the Global Ocean Pollution Index project does, and what data each one uses.

---

## 📁 Folder Structure

```
ocean_pollution_project/
├── data/        → all raw datasets (input)
├── src/         → Python scripts (the pipeline)
├── output/      → the website + final results
└── firebase.json → hosting config
```

---

## 🐍 src/ — The Python Pipeline

These scripts run in order. Each one feeds the next.

### `step1_load_and_explore.py`
Loads every raw dataset and prints a summary of each — column names, row counts, sample values. This is the inspection step, used to understand the data before processing it. Produces no output file; it just helps verify everything loaded correctly.

### `step2_merge.py`
The core script. It:
- Cleans and standardises all 12 data sources
- Maps each measurement to one of the 35 regions by its coordinates
- Fills missing values using published literature where needed
- Calculates the weighted pollution index (0–100) for each region
- **Output:** `output/master_ocean_pollution.csv`

### `step2b_historical_trends.py`
Calculates how fast microplastic pollution has historically grown in each region, using log-linear regression on 50 years of NOAA measurements (1972–2023). Regions without enough clean data fall back to a global average.
- **Output:** `output/region_growth_rates.csv`

### `step2c_combined_forecast.py`
Builds the per-region forecast to 2100 by blending three real sources:
- Microplastic trend (55%) — from step2b
- UN population growth (25%)
- IPCC ocean warming (20%)
- **Output:** updates `output/master_ocean_pollution.csv` with forecast columns

### `step3_dashboard.py`
Generates the interactive map dashboard from the master CSV. Builds the Leaflet map, the league table, the forecast chart, the year toggle, and the policy scenario slider.
- **Output:** `output/map.html`

---

## 📊 data/ — Raw Datasets (Input)

| File | Source | What it provides |
|---|---|---|
| `Marine_Microplastics_*.csv` | NOAA NCEI | Microplastic concentration measurements |
| `plastic-pollution-entering-the-ocean-through-rivers.csv` | Our World in Data | River plastic input by country |
| `UpdatedPub150.csv` | World Port Index (NGIA) | Global ports, locations, sizes |
| `GCC_socioeconomic.csv` | Copernicus / Zenodo | Coastal population within 10km |
| `cmems_mod_glo_bgc-car_*.nc` | Copernicus Marine | Ocean pH (acidification) |
| `woa23_all_o00mn01.csv` | NOAA World Ocean Atlas | Dissolved oxygen levels |
| `woa23_decav_t00mn01.csv` | NOAA World Ocean Atlas | Sea surface temperature |
| `incidents.csv` | NOAA IncidentNews | Oil spill incidents (location, volume) |
| `AQUASTAT Dissemination System.csv` | FAO AQUASTAT | Wastewater & agricultural runoff |
| `share-of-plastic-waste-that-is-mismanaged.csv` | OECD / Our World in Data | Plastic mismanagement rate |
| `scores.csv` | Ocean Health Index | Clean water & biodiversity scores |
| `WPP2024_Demographic_Indicators_Medium.csv` | UN | Population projections to 2100 |
| `tas_Global_yearly_*.nc` | IPCC CMIP6 | Temperature warming projections (SSP2-4.5) |
| `*_iuu_insights_*.csv` | Global Fishing Watch | Fishing activity (contextual) |

---

## 🌐 output/ — Website & Results

| File | What it is |
|---|---|
| `index.html` | Landing page — project intro, key findings, stats |
| `map.html` | Interactive dashboard — world map, league table, forecast chart, policy slider |
| `about.html` | Methodology page — data sources, weights, forecast explanation, limitations |
| `favicon.png` | The site logo (browser tab icon) |
| `master_ocean_pollution.csv` | Final scored dataset — 35 regions × all factors & forecasts |
| `region_growth_rates.csv` | Per-region historical growth rates |

---

## 🔢 The 12 Pollution Factors & Weights

| Factor | Weight | Source |
|---|---|---|
| Microplastics | 18% | NOAA |
| River plastic | 15% | Our World in Data |
| Dissolved oxygen | 10% | NOAA WOA |
| Port pressure | 9% | World Port Index |
| Coastal population | 8% | Copernicus |
| Oil spills | 7% | NOAA |
| Ocean pH | 7% | Copernicus |
| Sea temperature | 7% | NOAA WOA |
| Wastewater | 5% | FAO |
| Clean water (OHI) | 5% | Ocean Health Index |
| Biodiversity (OHI) | 5% | Ocean Health Index |
| Plastic mismanagement | 4% | OECD |

---

## ▶️ How to Run the Pipeline

```bash
python src/step2_merge.py
python src/step2b_historical_trends.py
python src/step2c_combined_forecast.py
python src/step3_dashboard.py
```

Then deploy the `output/` folder:
```bash
firebase deploy --only hosting
```

---

*Live site: oceanpollutionindex.com*
