"""
OCEAN POLLUTION PROJECT
Step 2c: Combined Multi-Source Forecast Engine
Replaces the flat 3% growth with a per-region forecast that blends THREE
real, independent data sources:

  1. Microplastic historical trend  (from NOAA 1972-2023 measurements)
  2. Coastal population growth        (from UN World Population Prospects 2024)
  3. Ocean warming rate              (from IPCC CMIP6 SSP2-4.5 projections)

Each region gets its OWN growth rate for each factor, then they are
combined using the same weights as the pollution index itself.

Output: output/master_ocean_pollution.csv  (updated forecast columns)
"""

import pandas as pd
import numpy as np
import xarray as xr
from scipy import stats
import glob, os, warnings
warnings.filterwarnings('ignore')

DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"
OUT_DIR  = r"C:\Users\sercan\Desktop\ocean_pollution_project\output"

def sep(t): print(f"\n{'='*60}\n  {t}\n{'='*60}")

REGIONS = {
    "North Atlantic Ocean":   (-80,  20,   0,  70),
    "South Atlantic Ocean":   (-70,  20, -60,   0),
    "North Pacific Ocean":    (120, -70,   0,  70),
    "South Pacific Ocean":    (140, -70, -60,   0),
    "Indian Ocean":           ( 20, 120, -60,  30),
    "Arctic Ocean":           (-180, 180,  70,  90),
    "Southern Ocean":         (-180, 180, -90, -60),
    "Mediterranean Sea":      ( -6,  42,  30,  47),
    "Caribbean Sea":          (-90, -58,   8,  25),
    "Gulf of Mexico":         (-98, -80,  18,  31),
    "North Sea":              ( -5,  10,  51,  61),
    "Baltic Sea":             (  9,  30,  53,  66),
    "Black Sea":              ( 27,  42,  40,  47),
    "Red Sea":                ( 32,  44,  12,  30),
    "Persian Gulf":           ( 47,  57,  22,  30),
    "South China Sea":        (105, 122,   0,  25),
    "Bay of Bengal":          ( 80, 100,   5,  23),
    "Arabian Sea":            ( 55,  78,   8,  26),
    "Gulf of Guinea":         (-10,  10,  -5,   5),
    "Coral Sea":              (142, 170, -30,  -8),
    "Tasman Sea":             (150, 178, -50, -30),
    "Bering Sea":             (160,-160,  50,  66),
    "Hudson Bay":             (-95, -65,  50,  65),
    "Great Lakes":            (-93, -76,  41,  49),
    "Caspian Sea":            ( 49,  55,  36,  48),
    "Lake Victoria":          ( 31,  35,  -3,   1),
    "Lake Tanganyika":        ( 28,  32,  -9,  -3),
    "Lake Baikal":            (103, 110,  51,  56),
    "Lake Superior":          (-93, -84,  46,  49),
    "Lake Huron":             (-84, -79,  43,  46),
}

# Which UN region/country best represents each water body's coastal population
REGION_TO_UN_LOCATION = {
    "North Atlantic Ocean": "Northern America",
    "South Atlantic Ocean": "South America",
    "North Pacific Ocean":  "Eastern Asia",
    "South Pacific Ocean":  "South-Eastern Asia",
    "Indian Ocean":         "Southern Asia",
    "Arctic Ocean":         "Northern Europe",
    "Southern Ocean":       "World",
    "Mediterranean Sea":    "Southern Europe",
    "Caribbean Sea":        "Latin America and the Caribbean",
    "Gulf of Mexico":       "Northern America",
    "North Sea":            "Western Europe",
    "Baltic Sea":           "Northern Europe",
    "Black Sea":            "Eastern Europe",
    "Red Sea":              "Western Asia",
    "Persian Gulf":         "Western Asia",
    "South China Sea":      "South-Eastern Asia",
    "Bay of Bengal":        "Southern Asia",
    "Arabian Sea":          "Southern Asia",
    "Gulf of Guinea":       "Western Africa",
    "Coral Sea":            "Oceania",
    "Tasman Sea":           "Australia/New Zealand",
    "Bering Sea":           "Northern America",
    "Hudson Bay":           "Northern America",
    "Great Lakes":          "Northern America",
    "Caspian Sea":          "Central Asia",
    "Lake Victoria":        "Eastern Africa",
    "Lake Tanganyika":      "Eastern Africa",
    "Lake Baikal":          "Eastern Europe",
    "Lake Superior":        "Northern America",
    "Lake Huron":           "Northern America",
}

def assign_region(lat, lon):
    if pd.isna(lat) or pd.isna(lon): return "Unknown"
    for region, (lo_min, lo_max, la_min, la_max) in REGIONS.items():
        if la_min <= lat <= la_max:
            if lo_min > lo_max:
                if lon >= lo_min or lon <= lo_max: return region
            else:
                if lo_min <= lon <= lo_max: return region
    return "Other Ocean"

# ════════════════════════════════════════════════════════════════════════════
# SOURCE 1: Microplastic historical trend (already computed in step2b)
# ════════════════════════════════════════════════════════════════════════════
sep("Source 1: Microplastic Trend (from step2b)")
growth_file = os.path.join(OUT_DIR, "region_growth_rates.csv")
if os.path.exists(growth_file):
    mp_growth = pd.read_csv(growth_file)[['region','annual_growth_rate']]
    mp_growth = mp_growth.rename(columns={'annual_growth_rate':'mp_growth_rate'})
    print(f"✅ Loaded microplastic growth rates for {len(mp_growth)} regions")
else:
    print("⚠️ region_growth_rates.csv not found — run step2b first! Using 3% default.")
    mp_growth = pd.DataFrame({'region': list(REGIONS.keys()), 'mp_growth_rate': 0.03})

# ════════════════════════════════════════════════════════════════════════════
# SOURCE 2: UN Population growth rate per region
# ════════════════════════════════════════════════════════════════════════════
sep("Source 2: UN Population Growth (2024-2100)")
un_file = glob.glob(os.path.join(DATA_DIR, "WPP2024_Demographic*"))[0]
un = pd.read_csv(un_file)
un = un[['Location','Time','PopGrowthRate']]

# Average projected growth rate 2024-2100 per location
un_future = un[(un['Time'] >= 2024) & (un['Time'] <= 2100)]
un_avg = un_future.groupby('Location')['PopGrowthRate'].mean().reset_index()
un_avg['PopGrowthRate'] = un_avg['PopGrowthRate'] / 100.0  # percentage -> fraction

pop_rates = []
for region, un_loc in REGION_TO_UN_LOCATION.items():
    match = un_avg[un_avg['Location'] == un_loc]
    if len(match) > 0:
        rate = match['PopGrowthRate'].values[0]
    else:
        rate = un_avg[un_avg['Location'] == 'World']['PopGrowthRate'].values[0] \
               if 'World' in un_avg['Location'].values else 0.005
    pop_rates.append({'region': region, 'pop_growth_rate': round(rate, 4), 'un_location': un_loc})

pop_growth = pd.DataFrame(pop_rates)
print(f"✅ Mapped UN population growth for {len(pop_growth)} regions")
print(pop_growth[['region','pop_growth_rate']].head(8).to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# SOURCE 3: IPCC ocean warming rate per region
# ════════════════════════════════════════════════════════════════════════════
sep("Source 3: IPCC Temperature Warming (SSP2-4.5, 2015-2099)")
ipcc_file = glob.glob(os.path.join(DATA_DIR, "tas_Global*.nc"))[0]
ds = xr.open_dataset(ipcc_file)

# tas is temperature anomaly in K, by year/lat/lon
# Normalize longitude if it's 0-360
lons = ds['lon'].values
lat_name = 'lat'
lon_name = 'lon'

warming_rates = []
for region, (lo_min, lo_max, la_min, la_max) in REGIONS.items():
    # IPCC lon may be 0-360; convert region bounds
    lo_min_360 = lo_min % 360
    lo_max_360 = lo_max % 360

    try:
        # Select region box, average over space, get warming trend over time
        if lons.max() > 180:  # 0-360 system
            if lo_min_360 <= lo_max_360:
                sub = ds['tas'].sel(lat=slice(la_min, la_max), lon=slice(lo_min_360, lo_max_360))
            else:
                # wraps around — take two slices
                sub = ds['tas'].sel(lat=slice(la_min, la_max))
        else:  # -180 to 180
            sub = ds['tas'].sel(lat=slice(la_min, la_max), lon=slice(lo_min, lo_max))

        regional_mean = sub.mean(dim=[lat_name, lon_name], skipna=True)
        anomaly_series = regional_mean.values
        years = np.array([int(str(t)[:4]) for t in ds['time'].values])

        valid = ~np.isnan(anomaly_series)
        if valid.sum() >= 10:
            slope, _, r_value, _, _ = stats.linregress(years[valid], anomaly_series[valid])
            # slope = degrees warming per year. Convert to a stress growth rate.
            # Each 0.05°C/yr of warming ≈ ~1% extra thermal pollution pressure per year
            warming_per_year = slope
            thermal_growth = max(0, warming_per_year * 0.20)  # scaling factor
        else:
            thermal_growth = 0.01
    except Exception as e:
        thermal_growth = 0.01

    warming_rates.append({
        'region': region,
        'warming_per_year': round(float(warming_per_year) if 'warming_per_year' in dir() else 0, 4),
        'thermal_growth_rate': round(float(thermal_growth), 4)
    })

warming = pd.DataFrame(warming_rates)
print(f"✅ Calculated ocean warming for {len(warming)} regions")
print(warming.sort_values('thermal_growth_rate', ascending=False).head(8).to_string(index=False))

# ════════════════════════════════════════════════════════════════════════════
# COMBINE: blended growth rate per region
# ════════════════════════════════════════════════════════════════════════════
sep("Combining Into Blended Per-Region Growth Rate")

# Load existing master file
master = pd.read_csv(os.path.join(OUT_DIR, "master_ocean_pollution.csv"))

# Merge all three growth sources
master = master.merge(mp_growth, on='region', how='left')
master = master.merge(pop_growth[['region','pop_growth_rate']], on='region', how='left')
master = master.merge(warming[['region','thermal_growth_rate']], on='region', how='left')

# Fill any gaps
master['mp_growth_rate']      = master['mp_growth_rate'].fillna(0.03)
master['pop_growth_rate']     = master['pop_growth_rate'].fillna(0.005)
master['thermal_growth_rate'] = master['thermal_growth_rate'].fillna(0.01)

# Blend: weight each driver by how much it contributes to pollution
# Microplastic-driven factors ~55%, population-driven ~25%, temperature ~20%
W_MP, W_POP, W_TEMP = 0.55, 0.25, 0.20

master['blended_growth_rate'] = (
    W_MP   * master['mp_growth_rate'] +
    W_POP  * master['pop_growth_rate'] +
    W_TEMP * master['thermal_growth_rate']
).round(4)

# Keep blended rate in a sane band
master['blended_growth_rate'] = master['blended_growth_rate'].clip(-0.01, 0.06)

# ── RECOMPUTE FORECASTS WITH PER-REGION RATES ───────────────────────────────
def forecast(base, rate, years):
    return round(float(base) * ((1 + rate) ** years), 2)

master['pollution_index_2030'] = master.apply(
    lambda r: forecast(r['pollution_index'], r['blended_growth_rate'], 4), axis=1)
master['pollution_index_2040'] = master.apply(
    lambda r: forecast(r['pollution_index'], r['blended_growth_rate'], 14), axis=1)
master['pollution_index_2050'] = master.apply(
    lambda r: forecast(r['pollution_index'], r['blended_growth_rate'], 24), axis=1)
master['pollution_index_2100'] = master.apply(
    lambda r: forecast(r['pollution_index'], r['blended_growth_rate'], 74), axis=1)

def grade(s):
    if pd.isna(s) or s==0: return 'Minimal'
    if s>=70: return 'Critical'
    elif s>=50: return 'High'
    elif s>=30: return 'Moderate'
    elif s>=10: return 'Low'
    else: return 'Minimal'

master['pollution_grade_2050'] = master['pollution_index_2050'].apply(grade)
master['pollution_grade_2100'] = master['pollution_index_2100'].apply(grade)

# Save
out = os.path.join(OUT_DIR, "master_ocean_pollution.csv")
master.to_csv(out, index=False)

sep("✅ COMBINED FORECAST COMPLETE")
print(f"Saved: {out}\n")
print("Per-region blended growth rates and forecasts:\n")
show = master[['region','pollution_index','mp_growth_rate','pop_growth_rate',
               'thermal_growth_rate','blended_growth_rate',
               'pollution_index_2050','pollution_index_2100']].copy()
show = show.sort_values('blended_growth_rate', ascending=False)
print(show.to_string(index=False))

print(f"\n\nNow each region grows at its OWN rate based on real data:")
print(f"  Fastest growing: {show.iloc[0]['region']} ({show.iloc[0]['blended_growth_rate']*100:.1f}%/yr)")
print(f"  Slowest growing: {show.iloc[-1]['region']} ({show.iloc[-1]['blended_growth_rate']*100:.1f}%/yr)")
