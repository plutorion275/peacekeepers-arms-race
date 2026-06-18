import pandas as pd
import os

dh = pd.read_csv("tables/nb06/section3_dumitrescu_hurlin.csv")
max_z = dh["Z"].abs().max()
print(f"Max |Z| after fix: {max_z:.3f}")
assert max_z < 1000, f"DH Z still exploding: {max_z}"
print(f"All Z finite: {dh['Z'].notna().all()}")
print()
print("Significant cells (p < 0.05) after fix:")
sig = dh[dh["p"] < 0.05]
if len(sig) == 0:
    print("  (None)")
else:
    print(sig[["weapon", "outcome", "lag", "Z", "p"]].to_string(index=False))
print()
print(f"Fig 2 exists: {os.path.exists('figures/nb06/fig2_dh_forest.png')}")
print(f"Fig 2 size:   {os.path.getsize('figures/nb06/fig2_dh_forest.png')} bytes")

placebo = pd.read_csv("tables/nb06/section4_placebo_comparison.csv")
print(f"\nPlacebo table rows: {len(placebo)} (expect 36)")
print(f"Placebo Z_mean max abs: {placebo['placebo_Z_mean'].abs().max():.3f}")
print("Done.")
