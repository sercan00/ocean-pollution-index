"""
OCEAN POLLUTION PROJECT
Step 2: Clean, Process & Merge All Datasets into Master File
v2 — adds dissolved oxygen, sea surface temperature, wastewater/agricultural
     runoff, and plastic mismanagement rate to the pollution index
"""

import pandas as pd
import numpy as np
import xarray as xr
import glob, os, warnings
warnings.filterwarnings('ignore')

DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"
OUT_DIR  = r"C:\Users\sercan\Desktop\ocean_pollution_project\output"
os.makedirs(OUT_DIR, exist_ok=True)

def sep(t): print(f"\n{'='*60}\n  {t}\n{'='*60}")

# ── REGION DEFINITIONS ───────────────────────────────────────────────────────
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

def assign_region(lat, lon):
    if pd.isna(lat) or pd.isna(lon): return "Unknown"
    for region, (lo_min, lo_max, la_min, la_max) in REGIONS.items():
        if la_min <= lat <= la_max:
            if lo_min > lo_max:
                if lon >= lo_min or lon <= lo_max: return region
            else:
                if lo_min <= lon <= lo_max: return region
    return "Other Ocean"

# ── LITERATURE VALUES FOR GAPS ───────────────────────────────────────────────
LITERATURE_MP = {
    "Black Sea":9.63,"South China Sea":1198.0,"Persian Gulf":339.5,
    "Bay of Bengal":365.8,"Caribbean Sea":296.0,"Gulf of Mexico":16.46,
    "Bering Sea":0.13,"Hudson Bay":0.22,"Great Lakes":111000.0,
    "Lake Superior":35000.0,"Lake Huron":111000.0,"North Sea":205.7,
    "Red Sea":45.0,"Coral Sea":2.5,"Tasman Sea":1.8,"Caspian Sea":15.0,
    "Lake Victoria":50.0,"Lake Tanganyika":8.0,"Lake Baikal":5.0,
    "Arabian Sea":45.0,"Gulf of Guinea":80.0,
}
LITERATURE_RIVER = {
    "South China Sea":580000,"Bay of Bengal":420000,"Arabian Sea":85000,
    "Gulf of Mexico":45000,"North Sea":12000,"Black Sea":35000,
    "Red Sea":3000,"Persian Gulf":8000,"Coral Sea":5000,"Tasman Sea":4000,
    "Bering Sea":2000,"Hudson Bay":3500,"Great Lakes":8000,"Caspian Sea":12000,
    "Lake Victoria":4500,"Lake Tanganyika":1200,"Lake Baikal":800,
    "Lake Superior":3000,"Lake Huron":4500,"Gulf of Guinea":18000,
    "Arctic Ocean":15000,"Southern Ocean":500,
}
LITERATURE_POP = {
    "South China Sea":85000000,"Bay of Bengal":120000000,"Arabian Sea":45000000,
    "Gulf of Mexico":35000000,"North Sea":28000000,"Black Sea":18000000,
    "Red Sea":8000000,"Persian Gulf":15000000,"Coral Sea":2500000,
    "Tasman Sea":8000000,"Bering Sea":500000,"Hudson Bay":300000,
    "Great Lakes":35000000,"Caspian Sea":12000000,"Lake Victoria":20000000,
    "Lake Tanganyika":3000000,"Lake Baikal":500000,"Lake Superior":4000000,
    "Lake Huron":6000000,"Gulf of Guinea":25000000,"Caribbean Sea":40000000,
    "Arctic Ocean":200000,"Southern Ocean":5000,
}

# ── HELPER: READ WOA23 CSV ───────────────────────────────────────────────────
def read_woa23_csv(filepath):
    """WOA23 CSVs have a metadata comment on line 1, headers on line 2."""
    try:
        df = pd.read_csv(filepath, skiprows=1, header=0)
        df.columns = [c.strip() for c in df.columns]
        # Standard WOA columns: lat, lon, depth, then data value
        # Rename first 3 cols to lat/lon/depth, rest are data
        cols = df.columns.tolist()
        # Find lat/lon columns (usually contain 'lat' or first two numeric cols)
        lat_col = [c for c in cols if 'lat' in c.lower()]
        lon_col = [c for c in cols if 'lon' in c.lower()]
        if lat_col and lon_col:
            df = df.rename(columns={lat_col[0]:'lat', lon_col[0]:'lon'})
        else:
            # Positional: col 0=lat, col 1=lon, col 2=depth, col 3=value
            df.columns = ['lat','lon','depth'] + list(df.columns[3:])
        return df
    except Exception as e:
        print(f"  ⚠️ Error reading {os.path.basename(filepath)}: {e}")
        return None

# ════════════════════════════════════════════════════════════════════════════
# EXISTING DATASETS
# ════════════════════════════════════════════════════════════════════════════

sep("Loading Microplastics (NOAA NCEI)")
mp_file = glob.glob(os.path.join(DATA_DIR, "Marine_Microplastics*.csv"))[0]
mp = pd.read_csv(mp_file)
mp = mp.rename(columns={'Latitude (degree)':'lat','Longitude (degree)':'lon',
    'Microplastics Measurement':'microplastic_value','Sample Date':'sample_date'})
mp['sample_date'] = pd.to_datetime(mp['sample_date'], errors='coerce')
mp['year'] = mp['sample_date'].dt.year
mp = mp[mp['microplastic_value'].notna()]
mp['region'] = mp.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
mp_agg = mp.groupby('region').agg(
    microplastic_mean=('microplastic_value','mean'),
    microplastic_max=('microplastic_value','max'),
    microplastic_sample_count=('microplastic_value','count'),
).reset_index()
print(f"✅ Microplastics: {len(mp_agg)} regions")

sep("Loading River Plastic (Our World in Data)")
river_file = glob.glob(os.path.join(DATA_DIR, "plastic-pollution-entering*.csv"))[0]
river = pd.read_csv(river_file)
river.columns = ['country','code','year','river_plastic_kg']
COUNTRY_REGION = {
    'United States':'North Atlantic Ocean','Canada':'North Atlantic Ocean',
    'United Kingdom':'North Atlantic Ocean','France':'North Atlantic Ocean',
    'Germany':'North Atlantic Ocean','Spain':'North Atlantic Ocean',
    'Portugal':'North Atlantic Ocean','Ireland':'North Atlantic Ocean',
    'Brazil':'South Atlantic Ocean','Argentina':'South Atlantic Ocean',
    'Nigeria':'South Atlantic Ocean','Angola':'South Atlantic Ocean',
    'South Africa':'South Atlantic Ocean',
    'India':'Indian Ocean','Bangladesh':'Indian Ocean',
    'Pakistan':'Indian Ocean','Myanmar':'Indian Ocean',
    'Tanzania':'Indian Ocean','Mozambique':'Indian Ocean',
    'Madagascar':'Indian Ocean','Kenya':'Indian Ocean',
    'China':'North Pacific Ocean','Japan':'North Pacific Ocean',
    'South Korea':'North Pacific Ocean','Russia':'North Pacific Ocean',
    'Indonesia':'South Pacific Ocean','Philippines':'South Pacific Ocean',
    'Vietnam':'South Pacific Ocean','Thailand':'South Pacific Ocean',
    'Malaysia':'South Pacific Ocean','Australia':'South Pacific Ocean',
    'Italy':'Mediterranean Sea','Greece':'Mediterranean Sea',
    'Turkey':'Mediterranean Sea','Egypt':'Mediterranean Sea',
    'Morocco':'Mediterranean Sea','Algeria':'Mediterranean Sea',
    'Mexico':'Caribbean Sea','Cuba':'Caribbean Sea',
    'Haiti':'Caribbean Sea','Dominican Republic':'Caribbean Sea',
    'Ghana':'Gulf of Guinea','Ivory Coast':'Gulf of Guinea',
    'Cameroon':'Gulf of Guinea','Democratic Republic of Congo':'Gulf of Guinea',
    'Sri Lanka':'Bay of Bengal',
    'Yemen':'Arabian Sea','Oman':'Arabian Sea','Somalia':'Arabian Sea',
}
river['region'] = river['country'].map(COUNTRY_REGION).fillna('Other Ocean')
river_agg = river.groupby('region').agg(
    river_plastic_kg_total=('river_plastic_kg','sum'),
).reset_index()
print(f"✅ River plastic: {len(river_agg)} regions")

sep("Loading World Port Index")
ports = pd.read_csv(os.path.join(DATA_DIR,"UpdatedPub150.csv"), encoding='latin1')
ports = ports.rename(columns={'Main Port Name':'port_name','Latitude':'lat',
    'Longitude':'lon','Harbor Size':'harbor_size'})
ports = ports[ports['lat'].notna() & ports['lon'].notna()]
ports['region'] = ports.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
size_w = {'Very Large':4,'Large':3,'Medium':2,'Small':1,'Very Small':0.5}
ports['port_weight'] = ports['harbor_size'].map(size_w).fillna(1)
port_agg = ports.groupby('region').agg(
    port_count=('port_name','count'),
    port_pressure_score=('port_weight','sum'),
).reset_index()
print(f"✅ Ports: {len(port_agg)} regions")

sep("Loading GCC Socioeconomic")
gcc = pd.read_csv(os.path.join(DATA_DIR,"GCC_socioeconomic.csv"))
gcc = gcc.rename(columns={'pop_10_m':'coastal_pop_10km','gdp_ppp_usd2017_2015':'gdp_usd'})
gcc = gcc[gcc['lat'].notna() & gcc['lon'].notna()]
gcc['region'] = gcc.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
gcc_agg = gcc.groupby('region').agg(
    coastal_pop_10km=('coastal_pop_10km','sum'),
    gdp_mean=('gdp_usd','mean'),
).reset_index()
print(f"✅ GCC: {len(gcc_agg)} regions")

sep("Loading Copernicus Biogeochemistry (pH)")
nc_file = glob.glob(os.path.join(DATA_DIR,"cmems_mod_glo_bgc*.nc"))[0]
ds = xr.open_dataset(nc_file)
ph_v = ds['ph'].isel(time=0, depth=0).values
lats = ds['latitude'].values
lons = ds['longitude'].values
LON2D, LAT2D = np.meshgrid(lons, lats)
nc_df = pd.DataFrame({'lat':LAT2D.flatten(),'lon':LON2D.flatten(),'ph':ph_v.flatten()})
nc_df = nc_df.dropna(subset=['ph'])
nc_df['region'] = nc_df.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
nc_agg = nc_df.groupby('region').agg(ph_mean=('ph','mean'), ph_min=('ph','min')).reset_index()
print(f"✅ Copernicus pH: {len(nc_agg)} regions")

# ════════════════════════════════════════════════════════════════════════════
# NEW DATASETS
# ════════════════════════════════════════════════════════════════════════════

sep("Loading WOA23 Dissolved Oxygen")
do_file = glob.glob(os.path.join(DATA_DIR, "woa23_all_o*.csv"))
if do_file:
    do_df = read_woa23_csv(do_file[0])
    if do_df is not None and 'lat' in do_df.columns and 'lon' in do_df.columns:
        # Get the surface value (first depth = shallowest)
        val_col = [c for c in do_df.columns if c not in ['lat','lon','depth']][0]
        do_df = do_df.rename(columns={val_col: 'dissolved_oxygen'})
        do_df['dissolved_oxygen'] = pd.to_numeric(do_df['dissolved_oxygen'], errors='coerce')
        do_df = do_df[do_df['dissolved_oxygen'].notna()]
        # Take surface layer only (depth == 0 or minimum depth)
        if 'depth' in do_df.columns:
            do_df['depth'] = pd.to_numeric(do_df['depth'], errors='coerce')
            min_depth = do_df['depth'].min()
            do_surface = do_df[do_df['depth'] == min_depth].copy()
        else:
            do_surface = do_df.copy()
        do_surface['region'] = do_surface.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
        do_agg = do_surface.groupby('region').agg(
            dissolved_oxygen_mean=('dissolved_oxygen','mean'),
            dissolved_oxygen_min=('dissolved_oxygen','min'),
        ).reset_index()
        print(f"✅ Dissolved Oxygen: {len(do_agg)} regions")
        print(f"   Sample: {do_agg.head(3).to_string()}")
    else:
        print("⚠️ Could not parse dissolved oxygen file — will impute")
        do_agg = pd.DataFrame({'region': list(REGIONS.keys())})
        do_agg['dissolved_oxygen_mean'] = np.nan
else:
    print("❌ Dissolved oxygen file not found")
    do_agg = pd.DataFrame({'region': list(REGIONS.keys())})
    do_agg['dissolved_oxygen_mean'] = np.nan

sep("Loading WOA23 Sea Surface Temperature")
sst_file = glob.glob(os.path.join(DATA_DIR, "woa23_decav_t*.csv"))
if sst_file:
    sst_df = read_woa23_csv(sst_file[0])
    if sst_df is not None and 'lat' in sst_df.columns and 'lon' in sst_df.columns:
        val_col = [c for c in sst_df.columns if c not in ['lat','lon','depth']][0]
        sst_df = sst_df.rename(columns={val_col: 'sst'})
        sst_df['sst'] = pd.to_numeric(sst_df['sst'], errors='coerce')
        sst_df = sst_df[sst_df['sst'].notna()]
        if 'depth' in sst_df.columns:
            sst_df['depth'] = pd.to_numeric(sst_df['depth'], errors='coerce')
            min_depth = sst_df['depth'].min()
            sst_surface = sst_df[sst_df['depth'] == min_depth].copy()
        else:
            sst_surface = sst_df.copy()
        sst_surface['region'] = sst_surface.apply(lambda r: assign_region(r['lat'], r['lon']), axis=1)
        sst_agg = sst_surface.groupby('region').agg(
            sst_mean=('sst','mean'),
            sst_max=('sst','max'),
        ).reset_index()
        # SST anomaly proxy: difference from expected baseline per region type
        # Open ocean baseline ~15°C, tropical ~28°C, polar ~0°C
        # We use deviation above 20°C as thermal stress signal
        sst_agg['sst_thermal_stress'] = (sst_agg['sst_mean'] - 20).clip(lower=0)
        print(f"✅ Sea Surface Temperature: {len(sst_agg)} regions")
        print(f"   Sample: {sst_agg[['region','sst_mean','sst_thermal_stress']].head(3).to_string()}")
    else:
        print("⚠️ Could not parse SST file — will impute")
        sst_agg = pd.DataFrame({'region': list(REGIONS.keys())})
        sst_agg['sst_mean'] = np.nan
        sst_agg['sst_thermal_stress'] = np.nan
else:
    print("❌ SST file not found")
    sst_agg = pd.DataFrame({'region': list(REGIONS.keys())})
    sst_agg['sst_mean'] = np.nan
    sst_agg['sst_thermal_stress'] = np.nan

sep("Loading AQUASTAT Wastewater & Agricultural Runoff")
aquastat_file = glob.glob(os.path.join(DATA_DIR, "AQUASTAT*.csv"))
if aquastat_file:
    aq = pd.read_csv(aquastat_file[0], encoding='utf-8-sig')
    print(f"   Variables available: {aq['Variable'].unique()[:5]}")
    # Filter for our variables
    ww = aq[aq['Variable'].str.contains('wastewater|municipal|withdrawal', case=False, na=False)]
    ww = ww[ww['Value'].notna()]
    # Map countries to regions
    ww['region'] = ww['Area'].map(COUNTRY_REGION).fillna('Other Ocean')
    ww_agg = ww.groupby('region').agg(
        wastewater_total=('Value','sum'),
        wastewater_countries=('Area','count'),
    ).reset_index()
    print(f"✅ AQUASTAT wastewater: {len(ww_agg)} regions")
else:
    print("❌ AQUASTAT file not found")
    ww_agg = pd.DataFrame({'region': list(REGIONS.keys())})
    ww_agg['wastewater_total'] = np.nan

sep("Loading Plastic Mismanagement Rate (Our World in Data)")
mismanage_file = glob.glob(os.path.join(DATA_DIR, "share-of-plastic-waste*.csv"))
if not mismanage_file:
    # Try in subdirectory
    mismanage_file = glob.glob(os.path.join(DATA_DIR, "share-of-plastic*", "*.csv"))
if mismanage_file:
    mm = pd.read_csv(mismanage_file[0])
    print(f"   Columns: {mm.columns.tolist()}")
    # Get most recent year per country
    mm = mm.sort_values('Year', ascending=False).drop_duplicates('Entity')
    val_col = [c for c in mm.columns if 'mismanag' in c.lower() or 'share' in c.lower() or 'plastic' in c.lower()]
    if val_col:
        mm = mm.rename(columns={val_col[0]: 'mismanagement_rate'})
        mm['region'] = mm['Entity'].map(COUNTRY_REGION).fillna('Other Ocean')
        mm_agg = mm.groupby('region').agg(
            mismanagement_rate_mean=('mismanagement_rate','mean'),
        ).reset_index()
        print(f"✅ Plastic mismanagement: {len(mm_agg)} regions")
    else:
        print(f"⚠️ Could not find value column in mismanagement file")
        mm_agg = pd.DataFrame({'region': list(REGIONS.keys())})
        mm_agg['mismanagement_rate_mean'] = np.nan
else:
    print("❌ Plastic mismanagement file not found")
    mm_agg = pd.DataFrame({'region': list(REGIONS.keys())})
    mm_agg['mismanagement_rate_mean'] = np.nan

# ════════════════════════════════════════════════════════════════════════════
# MERGE
# ════════════════════════════════════════════════════════════════════════════

sep("Merging into Master File")
master = pd.DataFrame({'region': list(REGIONS.keys())})
master = master.merge(mp_agg,    on='region', how='left')
master = master.merge(river_agg, on='region', how='left')
master = master.merge(port_agg,  on='region', how='left')
master = master.merge(gcc_agg,   on='region', how='left')
master = master.merge(nc_agg,    on='region', how='left')
master = master.merge(do_agg,    on='region', how='left')
master = master.merge(sst_agg,   on='region', how='left')
master = master.merge(ww_agg,    on='region', how='left')
master = master.merge(mm_agg,    on='region', how='left')

# ── FILL GAPS ────────────────────────────────────────────────────────────────
sep("Filling Gaps")
for idx, row in master.iterrows():
    r = row['region']
    if pd.isna(row['microplastic_mean']) and r in LITERATURE_MP:
        master.at[idx,'microplastic_mean'] = LITERATURE_MP[r]
    if pd.isna(row['river_plastic_kg_total']) and r in LITERATURE_RIVER:
        master.at[idx,'river_plastic_kg_total'] = LITERATURE_RIVER[r]
    if pd.isna(row['coastal_pop_10km']) and r in LITERATURE_POP:
        master.at[idx,'coastal_pop_10km'] = LITERATURE_POP[r]

# Fill remaining with medians
master['ph_mean'] = master['ph_mean'].fillna(8.05)
master['dissolved_oxygen_mean'] = master['dissolved_oxygen_mean'].fillna(
    master['dissolved_oxygen_mean'].median())
master['sst_thermal_stress'] = master['sst_thermal_stress'].fillna(0)
master['wastewater_total'] = master['wastewater_total'].fillna(0)
master['mismanagement_rate_mean'] = master['mismanagement_rate_mean'].fillna(
    master['mismanagement_rate_mean'].median())
for col in ['port_count','port_pressure_score']:
    if col in master.columns:
        master[col] = master[col].fillna(0)

print("✅ Gaps filled")

# ── UPDATED POLLUTION INDEX ───────────────────────────────────────────────────
sep("Calculating Updated Pollution Index")

def normalize(s):
    mn, mx = s.min(), s.max()
    return (s - mn) / (mx - mn) * 100 if mx != mn else s * 0

# Dissolved oxygen: LOWER is worse (oxygen depletion = more polluted)
master['score_microplastic']  = normalize(master['microplastic_mean'].fillna(0))
master['score_river']         = normalize(master['river_plastic_kg_total'].fillna(0))
master['score_port']          = normalize(master['port_pressure_score'].fillna(0))
master['score_population']    = normalize(master['coastal_pop_10km'].fillna(0))
master['score_ph']            = normalize(7.5 - master['ph_mean'].fillna(8.1))
master['score_oxygen']        = normalize(
    master['dissolved_oxygen_mean'].max() - master['dissolved_oxygen_mean'].fillna(
        master['dissolved_oxygen_mean'].median()))
master['score_temperature']   = normalize(master['sst_thermal_stress'].fillna(0))
master['score_wastewater']    = normalize(master['wastewater_total'].fillna(0))
master['score_mismanagement'] = normalize(master['mismanagement_rate_mean'].fillna(0))

# Updated weights — sum to 1.0
# Reduced existing weights slightly to make room for new factors
W = {
    'microplastic':  0.22,
    'river':         0.18,
    'port':          0.12,
    'population':    0.10,
    'ph':            0.08,
    'oxygen':        0.12,  # NEW — oxygen depletion
    'temperature':   0.08,  # NEW — thermal stress
    'wastewater':    0.06,  # NEW — agricultural/municipal runoff
    'mismanagement': 0.04,  # NEW — plastic waste management
}

master['pollution_index'] = (
    W['microplastic']  * master['score_microplastic']  +
    W['river']         * master['score_river']         +
    W['port']          * master['score_port']          +
    W['population']    * master['score_population']    +
    W['ph']            * master['score_ph']            +
    W['oxygen']        * master['score_oxygen']        +
    W['temperature']   * master['score_temperature']   +
    W['wastewater']    * master['score_wastewater']    +
    W['mismanagement'] * master['score_mismanagement']
).round(2)

def grade(s):
    if pd.isna(s) or s==0: return 'Minimal'
    if s>=70: return 'Critical'
    elif s>=50: return 'High'
    elif s>=30: return 'Moderate'
    elif s>=10: return 'Low'
    else: return 'Minimal'

master['pollution_grade']        = master['pollution_index'].apply(grade)
master['pollution_index_2030']   = (master['pollution_index'] * (1.03**4)).round(2)
master['pollution_index_2040']   = (master['pollution_index'] * (1.03**14)).round(2)
master['pollution_index_2050']   = (master['pollution_index'] * (1.03**24)).round(2)
master['pollution_index_2100']   = (master['pollution_index'] * (1.03**74)).round(2)
master['pollution_grade_2050']   = master['pollution_index_2050'].apply(grade)
master['pollution_grade_2100']   = master['pollution_index_2100'].apply(grade)

out = os.path.join(OUT_DIR, "master_ocean_pollution.csv")
master.to_csv(out, index=False)

sep("✅ MASTER FILE CREATED — v2")
print(f"Saved: {out}")
print(f"Shape: {master.shape}")
print(f"\nNew factors included: Dissolved Oxygen, SST Thermal Stress, Wastewater, Plastic Mismanagement")
print(f"\nTop 10 most polluted regions (2026):")
cols = ['region','pollution_index','pollution_grade',
        'dissolved_oxygen_mean','sst_mean',
        'wastewater_total','mismanagement_rate_mean',
        'pollution_index_2050','pollution_index_2100']
print(master[[c for c in cols if c in master.columns]
    ].sort_values('pollution_index',ascending=False).head(10).to_string(index=False))

print(f"\nRegions still missing microplastic data:")
miss = master[master['microplastic_mean'].isna()]['region'].tolist()
print(miss if miss else "None ✅")
