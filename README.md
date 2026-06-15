# 🌊 Global Ocean Pollution Index

A data science project that measures, scores, and forecasts pollution levels across **35 major water bodies** — oceans, seas, and large lakes — using 12 real-world factors and a weighted multi-factor model.

**Live dashboard:** [oceanpollutionindex.com](https://oceanpollutionindex.com)

---

## 📊 What It Does

- Aggregates 12 pollution factors — microplastics, river plastic, dissolved oxygen, port pressure, coastal population, oil spills, ocean pH, sea temperature, wastewater, clean water, biodiversity, and plastic mismanagement — into a single **Pollution Index (0–100)** per water body
- Forecasts pollution trajectories to **2030, 2050, and 2100** using a per-region model that blends measured trends, population growth, and ocean warming
- Visualises everything on an **interactive dark-mode world map** with a year toggle (2026 / 2050 / 2100) and a **policy scenario slider** that shows how the future changes under different levels of action

---

## 🗂️ Data Sources

| Dataset | Source | What it contributes |
|---|---|---|
| Marine Microplastics | NOAA NCEI | Direct pollution measurement |
| River Plastic Input | Our World in Data / Meijer et al. | Land-to-ocean pollution pathways |
| Dissolved Oxygen | NOAA World Ocean Atlas | Dead zones / oxygen depletion |
| World Port Index | NGIA | Industrial coastal pressure |
| Coastal Population | Copernicus / Zenodo | Coastal population density |
| Oil Spills | NOAA IncidentNews | Spill frequency and volume |
| Ocean Biogeochemistry | Copernicus Marine Service | Ocean pH (acidification) |
| Sea Surface Temperature | NOAA World Ocean Atlas | Thermal stress |
| Wastewater & Runoff | FAO AQUASTAT | Municipal and agricultural runoff |
| Clean Water & Biodiversity | Ocean Health Index | Independent ecosystem health scores |
| Plastic Mismanagement | OECD / Our World in Data | Share of badly disposed plastic |
| Population Projections | UN World Population Prospects | Forecast population growth to 2100 |
| Climate Projections | IPCC CMIP6 (SSP2-4.5) | Forecast ocean warming to 2100 |

Missing values were filled using published peer-reviewed literature (cited in `src/step2_merge.py`) or statistical imputation from comparable regions, with source flagged per region.

---

## 🧮 Pollution Index Methodology

The index is a weighted composite of 12 normalised (0–100) factors:

| Factor | Weight |
|---|---|
| Microplastic concentration | 18% |
| River plastic input | 15% |
| Dissolved oxygen depletion | 10% |
| Port & shipping pressure | 9% |
| Coastal population | 8% |
| Oil spill pressure | 7% |
| Ocean pH (acidification) | 7% |
| Sea surface temperature | 7% |
| Wastewater & runoff | 5% |
| Clean water (OHI) | 5% |
| Biodiversity (OHI) | 5% |
| Plastic mismanagement | 4% |

### Forecasting

Rather than one growth rate for every region, each water body is forecast using its **own growth rate**, blended from three independent real-world sources:

- **Microplastic trend (55%)** — log-linear regression on 50 years of NOAA measurements (1972–2023)
- **Population growth (25%)** — UN projections per region to 2100
- **Ocean warming (20%)** — IPCC CMIP6 temperature projections per region

This means regions with rising plastic, growing population, and rapid warming climb steeply — while regions like the Mediterranean (declining plastic trend, shrinking population) are projected to improve.

---

## 🗺️ Key Findings

- **North Pacific** ranks highest in 2026 — lowest ocean pH of any basin, plus the highest concentration of recorded oil spill incidents
- **Indian Ocean** carries the highest coastal population pressure — 208 million people within 10km of shore
- **Great Lakes** (Erie, Ontario, Michigan) rank above most oceans, driven by extreme microplastic densities
- **Arctic Ocean** shows a low score today but is warming faster than any region on the map
- **Mediterranean** is one of the few water bodies projected to *improve* by 2100

---

## 🛠️ Tech Stack

- **Python** — pandas, numpy, xarray, scipy, netCDF4
- **Visualisation** — Leaflet.js, Chart.js (vanilla HTML/JS, no framework)
- **Data formats** — CSV, NetCDF, GeoJSON, Shapefile
- **Hosting** — Firebase Hosting, GoDaddy domain

---

## 📁 Project Structure

```
ocean_pollution_project/
├── data/                              # All raw datasets
├── src/
│   ├── step1_load_and_explore.py      # Data audit and exploration
│   ├── step2_merge.py                 # Cleaning, gap-filling, index calculation
│   ├── step2b_historical_trends.py    # Per-region growth rates from history
│   ├── step2c_combined_forecast.py    # 3-source blended forecast
│   └── step3_dashboard.py             # Interactive HTML dashboard generator
├── output/
│   ├── master_ocean_pollution.csv     # Final merged dataset (35 regions)
│   ├── index.html                     # Landing page
│   ├── map.html                       # Interactive dashboard
│   └── about.html                     # Methodology page
└── requirements.txt
```

---

## 🚀 Run It Yourself

```bash
pip install -r requirements.txt
python src/step2_merge.py               # generates master_ocean_pollution.csv
python src/step2b_historical_trends.py  # generates region_growth_rates.csv
python src/step2c_combined_forecast.py  # adds forecast columns
python src/step3_dashboard.py           # generates map.html
```

Then open `output/index.html` in any browser.

---

## 📌 Limitations & Future Work

- The factor weights are chosen by reasoning about relevance, not derived statistically — a common approach for composite indices, but a subjective one
- Microplastic units vary across studies (items/m³, items/kg, items/km²); normalisation is approximate
- Oil spill data is strongest for US coastal waters (NOAA), so some regions are likely under-represented
- Forecasts assume current trends continue; they are trajectories, not predictions
- A more sophisticated time-series model (Prophet, LSTM) would improve forecast accuracy

---

*Built by Sercan Emiroglu — BSc Computer Science, City St George's, University of London*
