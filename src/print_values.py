"""Print exact current values for the landing page."""
import pandas as pd
import os

OUT_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\output"
m = pd.read_csv(os.path.join(OUT_DIR, "master_ocean_pollution.csv"))

def g(region, col):
    v = m[m['region']==region][col].values
    return v[0] if len(v) else None

print("=== TOP REGIONS BY POLLUTION INDEX ===")
top = m.sort_values('pollution_index', ascending=False)[
    ['region','pollution_index','pollution_index_2050','pollution_index_2100','pollution_grade']].head(8)
print(top.to_string(index=False))

print("\n=== KEY REGION VALUES FOR LANDING PAGE ===")
for r in ['Indian Ocean','Great Lakes','South China Sea','North Pacific Ocean','Arctic Ocean','North Atlantic Ocean']:
    pi = g(r,'pollution_index')
    p50 = g(r,'pollution_index_2050')
    p100 = g(r,'pollution_index_2100')
    p30 = g(r,'pollution_index_2030')
    print(f"\n{r}:")
    print(f"  2026: {pi}, 2030: {p30}, 2050: {p50}, 2100: {p100}")
    print(f"  microplastic_mean: {g(r,'microplastic_mean')}")
    print(f"  coastal_pop_10km: {g(r,'coastal_pop_10km')}")
    print(f"  ph_mean: {g(r,'ph_mean')}")

print("\n=== TOTAL MEASUREMENTS ===")
print(f"Microplastic sample count total: {m['microplastic_sample_count'].sum()}")
