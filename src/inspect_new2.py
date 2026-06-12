"""Inspect the Ocean Health Index and NOAA oil spill files."""
import pandas as pd
import glob, os

DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"

print("="*60)
print("  FILES IN DATA FOLDER (csv)")
print("="*60)
for f in glob.glob(os.path.join(DATA_DIR, "*.csv")):
    print(" ", os.path.basename(f))

print("\n" + "="*60)
print("  OCEAN HEALTH INDEX")
print("="*60)
# OHI file could be named scores.csv or similar
ohi_candidates = glob.glob(os.path.join(DATA_DIR, "*score*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*ohi*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*OHI*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*health*.csv"))
if ohi_candidates:
    ohi = pd.read_csv(ohi_candidates[0])
    print(f"File: {os.path.basename(ohi_candidates[0])}")
    print(f"Shape: {ohi.shape}")
    print(f"Columns: {ohi.columns.tolist()}")
    print(ohi.head(5).to_string())
else:
    print("Not found automatically. CSV files above — tell me which is the OHI one.")

print("\n" + "="*60)
print("  NOAA OIL SPILLS (IncidentNews)")
print("="*60)
oil_candidates = glob.glob(os.path.join(DATA_DIR, "*incident*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*Incident*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*spill*.csv")) + \
                 glob.glob(os.path.join(DATA_DIR, "*oil*.csv"))
if oil_candidates:
    oil = pd.read_csv(oil_candidates[0])
    print(f"File: {os.path.basename(oil_candidates[0])}")
    print(f"Shape: {oil.shape}")
    print(f"Columns: {oil.columns.tolist()}")
    print(oil.head(5).to_string())
else:
    print("Not found automatically. CSV files above — tell me which is the oil spill one.")
