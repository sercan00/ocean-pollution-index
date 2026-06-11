"""Quick check of the UN population and IPCC temperature files."""
import pandas as pd
import xarray as xr
import glob, os

DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"

print("="*60)
print("  UN POPULATION FILE")
print("="*60)
un_file = glob.glob(os.path.join(DATA_DIR, "WPP2024_Demographic*"))
if un_file:
    # try reading as gzip csv
    try:
        un = pd.read_csv(un_file[0], compression='gzip', nrows=5)
    except:
        un = pd.read_csv(un_file[0], nrows=5)
    print(f"File: {os.path.basename(un_file[0])}")
    print(f"Columns: {un.columns.tolist()}")
    print(un[['Location','Time','TPopulation1July','PopGrowthRate'] if 'TPopulation1July' in un.columns else un.columns[:8]].head())
else:
    print("Not found")

print("\n" + "="*60)
print("  IPCC TEMPERATURE NETCDF")
print("="*60)
nc_file = glob.glob(os.path.join(DATA_DIR, "tas_Global*.nc"))
if nc_file:
    ds = xr.open_dataset(nc_file[0])
    print(f"File: {os.path.basename(nc_file[0])}")
    print(f"Variables: {list(ds.data_vars)}")
    print(f"Dimensions: {dict(ds.dims)}")
    print(f"Coordinates: {list(ds.coords)}")
    # Check time range
    if 'time' in ds.coords:
        print(f"Time range: {ds.time.values[0]} to {ds.time.values[-1]}")
else:
    print("Not found")
