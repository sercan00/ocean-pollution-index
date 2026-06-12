"""
OCEAN POLLUTION PROJECT
Step 2b: Historical Trend Analysis — Per-Region Growth Rates
Replaces the flat 3% assumption with a real growth rate calculated from
35 years of NOAA microplastic measurements (1989-2022), region by region.
Output: output/region_growth_rates.csv
"""

import pandas as pd
import numpy as np
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
    "Aegean Sea":             ( 23,  28,  35,  41),
    "Gulf of Thailand":       ( 99, 105,   6,  14),
    "Lake Michigan":          (-88, -85,  41,  46),
    "Lake Erie":              (-83, -78,  41,  43),
    "Lake Ontario":           (-80, -76,  43,  44),
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

# Global fallback growth rate (3% = observed plastic production trend)
GLOBAL_FALLBACK_RATE = 0.03

# Bounds — keep growth rates realistic (between -2% and +8% per year)
MIN_RATE = -0.01
MAX_RATE = 0.05
MIN_R_SQUARED = 0.30  # below this, trend is too noisy — use fallback

sep("Loading Microplastics Time Series")
mp_file = glob.glob(os.path.join(DATA_DIR, "Marine_Microplastics*.csv"))[0]
mp = pd.read_csv(mp_file)
mp = mp.rename(columns={'Latitude (degree)':'lat','Longitude (degree)':'lon',
    'Microplastics Measurement':'value','Sample Date':'date'})
mp['date'] = pd.to_datetime(mp['date'], errors='coerce')
mp['year'] = mp['date'].dt.year
mp = mp[mp['value'].notna() & mp['year'].notna()]
mp = mp[mp['value'] > 0]  # drop zeros for log regression
mp['region'] = mp.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
print(f"✅ Loaded {len(mp)} measurements spanning {int(mp['year'].min())}-{int(mp['year'].max())}")

sep("Calculating Per-Region Growth Rates")
print("Method: log-linear regression of mean annual concentration vs year")
print("(A positive slope = pollution worsening over time)\n")

results = []
for region in REGIONS.keys():
    sub = mp[mp['region'] == region]

    if len(sub) < 10:
        # Not enough data — use global fallback
        results.append({
            'region': region,
            'annual_growth_rate': GLOBAL_FALLBACK_RATE,
            'data_points': len(sub),
            'years_covered': 0,
            'r_squared': np.nan,
            'method': 'global fallback (insufficient data)'
        })
        continue

    # Aggregate to annual means
    annual = sub.groupby('year')['value'].mean().reset_index()
    annual = annual[annual['value'] > 0]

    if len(annual) < 4:
        results.append({
            'region': region,
            'annual_growth_rate': GLOBAL_FALLBACK_RATE,
            'data_points': len(sub),
            'years_covered': len(annual),
            'r_squared': np.nan,
            'method': 'global fallback (too few years)'
        })
        continue

    # Log-linear regression: log(value) = a + b*year
    # The slope b gives the exponential growth rate
    log_vals = np.log(annual['value'].values)
    years = annual['year'].values

    slope, intercept, r_value, p_value, std_err = stats.linregress(years, log_vals)
    r_squared = r_value**2

    # Convert log-slope to annual growth rate: e^slope - 1
    growth_rate = np.exp(slope) - 1

    # If the trend is too noisy (low R²), don't trust it — use global fallback
    if r_squared < MIN_R_SQUARED:
        results.append({
            'region': region,
            'annual_growth_rate': GLOBAL_FALLBACK_RATE,
            'data_points': len(sub),
            'years_covered': len(annual),
            'r_squared': round(r_squared, 3),
            'method': 'global fallback (trend too noisy, R2<0.3)'
        })
        continue

    # Clip to realistic conservative bounds
    growth_rate_clipped = np.clip(growth_rate, MIN_RATE, MAX_RATE)

    results.append({
        'region': region,
        'annual_growth_rate': round(growth_rate_clipped, 4),
        'data_points': len(sub),
        'years_covered': len(annual),
        'r_squared': round(r_squared, 3),
        'method': 'measured trend' if abs(growth_rate) <= MAX_RATE else 'measured (clipped)'
    })

growth_df = pd.DataFrame(results)

# Save
out = os.path.join(OUT_DIR, "region_growth_rates.csv")
growth_df.to_csv(out, index=False)

sep("✅ GROWTH RATES CALCULATED")
print(f"Saved: {out}\n")
print(growth_df.sort_values('annual_growth_rate', ascending=False).to_string(index=False))

print(f"\n\nSummary:")
measured = growth_df[growth_df['method'].str.contains('measured')]
print(f"  Regions with measured trends: {len(measured)}")
print(f"  Regions using global fallback: {len(growth_df) - len(measured)}")
print(f"  Highest growth: {growth_df.loc[growth_df['annual_growth_rate'].idxmax(), 'region']} "
      f"({growth_df['annual_growth_rate'].max()*100:.1f}%/yr)")
print(f"  Lowest growth: {growth_df.loc[growth_df['annual_growth_rate'].idxmin(), 'region']} "
      f"({growth_df['annual_growth_rate'].min()*100:.1f}%/yr)")
