"""Check what goals and dimensions exist in OHI scores."""
import pandas as pd, os
DATA_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\data"
ohi = pd.read_csv(os.path.join(DATA_DIR, "scores.csv"))

print("=== GOALS available ===")
print(ohi[['goal','long_goal']].drop_duplicates().to_string(index=False))
print("\n=== DIMENSIONS available ===")
print(ohi['dimension'].unique())
print("\n=== SCENARIOS (years) available ===")
print(sorted(ohi['scenario'].unique()))
print("\n=== Sample: Clean Waters (CW) score dimension, latest year ===")
latest = ohi['scenario'].max()
cw = ohi[(ohi['goal']=='CW') & (ohi['dimension']=='score') & (ohi['scenario']==latest)]
print(f"Latest year: {latest}, rows: {len(cw)}")
print(cw[['region_name','value']].head(10).to_string(index=False))
