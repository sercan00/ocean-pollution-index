# 🌊 Global Ocean Pollution Index

A data science project that measures, scores, and forecasts pollution levels across **30 major water bodies** — oceans, seas, and large lakes — using 6 real-world datasets and a weighted multi-factor model.

**Live dashboard:** [oceanpollutionindex.com](https://oceanpollutionindex.com)

---

## 📊 What It Does

- Aggregates microplastic measurements, river plastic input, port industrial pressure, coastal population density, and ocean pH into a single **Pollution Index (0–100)** per water body
- Forecasts pollution trajectories to **2030, 2040, 2050, and 2100** using compound growth modelling
- Visualises everything on an **interactive dark-mode world map** with year toggle (2026 / 2050 / 2100)

---

## 🗂️ Data Sources

| Dataset | Source | What it contributes |
|---|---|---|
| Marine Microplastics | NOAA NCEI | Direct pollution measurement |
| River Plastic Input | Our World in Data / Meijer et al. | Land-to-ocean pollution pathways |
| World Port Index | NGIA / Kaggle | Industrial coastal pressure |
| Global Coastal Characteristics | Copernicus / Zenodo | Coastal population density, GDP |
| Ocean Biogeochemistry | Copernicus Marine Service | Ocean pH, dissolved carbon |
| IUU Fishing Risk | Global Fishing Watch | Fishing pressure, illegal activity |

Missing values were filled using published peer-reviewed literature (cited in `src/step2_merge.py`) or statistical imputation from comparable regions, with source flagged per region.

---

## 🧮 Pollution Index Methodology

The index is a weighted composite of 5 normalised (0–100) components:

| Component | Weight | Rationale |
|---|---|---|
| Microplastic concentration | 30% | Direct, measurable pollution |
| River plastic input (kg/yr) | 25% | Primary ocean pollution pathway |
| Port pressure score | 20% | Industrial and shipping activity |
| Coastal population (10km) | 15% | Proxy for waste generation |
| Ocean pH deviation | 10% | Acidification from CO₂ absorption |

Forecasts assume a **3% annual compound increase** — consistent with observed global plastic production growth trends.

---

## 🗺️ Key Findings

- **Great Lakes** and **South China Sea** rank highest in 2026 due to exceptional microplastic particle densities and river input from major urban watersheds
- **Indian Ocean** carries the highest coastal population pressure — 208 million people within 10km of shore
- By 2100, all major water bodies cross into **Critical** territory under current trajectory
- **Arctic Ocean** and **Southern Ocean** show low current scores but are receiving increasing microplastic transport via ocean currents

---

## 🛠️ Tech Stack

- **Python** — pandas, numpy, xarray, geopandas, scikit-learn, netCDF4
- **Visualisation** — Leaflet.js, Chart.js (vanilla HTML/JS, no framework)
- **Data formats** — CSV, NetCDF, GeoJSON, Shapefile
- **Hosting** — Netlify (static), GoDaddy domain

---

## 📁 Project Structure

```
ocean_pollution_project/
├── data/                         # All raw datasets
├── src/
│   ├── step1_load_and_explore.py # Data audit and exploration
│   ├── step2_merge.py            # Cleaning, gap-filling, index calculation
│   └── step3_dashboard.py        # Interactive HTML dashboard generator
├── output/
│   ├── master_ocean_pollution.csv # Final merged dataset (30 regions × 34 columns)
│   └── index.html                 # Live dashboard
└── requirements.txt
```

---

## 🚀 Run It Yourself

```bash
pip install -r requirements.txt
python src/step2_merge.py      # generates master_ocean_pollution.csv
python src/step3_dashboard.py  # generates index.html
```

Then open `output/index.html` in any browser.

---

## 📌 Limitations & Future Work

- Copernicus biogeochemistry snapshot is a single date (June 2026); future versions should use multi-year averages
- Forecast model assumes linear compound growth; a more sophisticated time-series model (Prophet, LSTM) would improve accuracy
- AIS shipping density data (Global Fishing Watch) not yet integrated — planned for v2
- Microplastic units vary across studies (items/m³, items/kg, items/km²); normalisation is approximate

---

*Built by Sercan Emiroglu — BSc Computer Science, City St George's University of London*
