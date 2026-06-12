"""Print exact current values for updating the website pages."""
import pandas as pd, os
OUT_DIR = r"C:\Users\sercan\Desktop\ocean_pollution_project\output"
m = pd.read_csv(os.path.join(OUT_DIR, "master_ocean_pollution.csv"))

def g(region, col):
    v = m[m['region']==region][col].values
    return v[0] if len(v) else None

print("=== TOP 6 BY POLLUTION INDEX (2026) ===")
top = m.sort_values('pollution_index', ascending=False)[
    ['region','pollution_index','pollution_index_2050','pollution_index_2100','pollution_grade']].head(6)
print(top.to_string(index=False))

print("\n=== SPECIFIC VALUES FOR LANDING PAGE CARDS ===")
for r in ['North Pacific Ocean','Indian Ocean','Great Lakes','South China Sea','Arctic Ocean']:
    print(f"\n{r}:")
    print(f"  2026={g(r,'pollution_index')}, 2030={g(r,'pollution_index_2030')}, 2050={g(r,'pollution_index_2050')}, 2100={g(r,'pollution_index_2100')}")
    print(f"  grade={g(r,'pollution_grade')}, pH={g(r,'ph_mean')}")
    print(f"  coastal_pop={g(r,'coastal_pop_10km')}, microplastic={g(r,'microplastic_mean')}")
    print(f"  oil_spill_pressure={g(r,'oil_spill_pressure')}")

print(f"\n=== Total microplastic measurements ===")
print(f"{m['microplastic_sample_count'].sum():.0f}")

print(f"\n=== Factor count ===")
print("12 factors now")
