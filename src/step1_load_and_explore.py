"""
OCEAN POLLUTION PROJECT
Step 1: Load & Explore All Datasets
Run this first to confirm every file loads correctly and see what columns you have.
"""

import pandas as pd
import numpy as np
import xarray as xr
import glob
import os
import warnings
warnings.filterwarnings('ignore')

# ── CONFIG: point this to your data folder ──────────────────────────────────
DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"  # CHANGE IF NEEDED
# ────────────────────────────────────────────────────────────────────────────

def sep(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)

# ── 1. NOAA Marine Microplastics ─────────────────────────────────────────────
sep("1. NOAA Marine Microplastics")
microplastics_file = glob.glob(os.path.join(DATA_DIR, "Marine_Microplastics*.csv"))
if microplastics_file:
    mp = pd.read_csv(microplastics_file[0])
    print(f"Shape: {mp.shape}")
    print(f"Columns: {mp.columns.tolist()}")
    print(mp.head(3))
else:
    print("❌ File not found! Check filename.")

# ── 2. GCC Socioeconomic (Coastal Population, Ports, GDP) ────────────────────
sep("2. GCC Socioeconomic")
gcc_file = os.path.join(DATA_DIR, "GCC_socioeconomic.csv")
if os.path.exists(gcc_file):
    gcc = pd.read_csv(gcc_file, nrows=5)
    print(f"Columns: {gcc.columns.tolist()}")
    print(gcc.head(3))
else:
    print("❌ File not found!")

# ── 3. River Plastic Input (Our World in Data) ───────────────────────────────
sep("3. River Plastic Into Ocean")
river_file = glob.glob(os.path.join(DATA_DIR, "plastic-pollution-entering*.csv"))
if river_file:
    river = pd.read_csv(river_file[0])
    print(f"Shape: {river.shape}")
    print(f"Columns: {river.columns.tolist()}")
    print(river.head(5))
else:
    print("❌ File not found!")

# ── 4. World Port Index ──────────────────────────────────────────────────────
sep("4. World Port Index")
port_file = os.path.join(DATA_DIR, "UpdatedPub150.csv")
if os.path.exists(port_file):
    ports = pd.read_csv(port_file, encoding='latin1')
    print(f"Shape: {ports.shape}")
    print(f"Columns: {ports.columns.tolist()}")
    print(ports[['Main Port Name', 'Latitude', 'Longitude', 'Country Code', 'World Water Body', 'Harbor Size']].head(5))
else:
    print("❌ File not found!")

# ── 5. Shipping Lanes ────────────────────────────────────────────────────────
sep("5. Shipping Lanes")
shipping_dir = os.path.join(DATA_DIR, "Shipping-Lanes-main", "Shipping-Lanes-main", "data")
if os.path.exists(shipping_dir):
    files = os.listdir(shipping_dir)
    print(f"Files in shipping data folder: {files}")
else:
    print("❌ Folder not found! Check path.")

# ── 6. IUU Fishing (Global Fishing Watch) ───────────────────────────────────
sep("6. IUU Fishing Risk (most recent year)")
iuu_files = sorted(glob.glob(os.path.join(DATA_DIR, "*iuu_insights*.csv")))
if iuu_files:
    print(f"Found {len(iuu_files)} yearly files: {[os.path.basename(f) for f in iuu_files]}")
    iuu_latest = pd.read_csv(iuu_files[-1], nrows=5)
    print(f"Columns: {iuu_latest.columns.tolist()}")
    print(iuu_latest.head(3))
else:
    print("❌ Files not found!")

# ── 7. Copernicus Biogeochemistry (NetCDF) ───────────────────────────────────
sep("7. Copernicus Biogeochemistry (NetCDF)")
nc_file = glob.glob(os.path.join(DATA_DIR, "cmems_mod_glo_bgc*.nc"))
if nc_file:
    ds = xr.open_dataset(nc_file[0])
    print(f"Variables: {list(ds.data_vars)}")
    print(f"Dimensions: {dict(ds.dims)}")
    print(f"Coordinates: {list(ds.coords)}")
    print(ds)
else:
    print("❌ NetCDF file not found!")

print("\n✅ Exploration complete. Check above for any ❌ errors.")
print("If all 7 loaded OK, run step2_merge.py next.")
