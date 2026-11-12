import sys
sys.path.insert(0, r".\app")

import pandas as pd
from inference import tier2_predict

df = pd.read_csv(r".\dataset\val_split.csv")

rows = []

for r in df.itertuples():
    p = tier2_predict(r.code)

    rows.append({
        "true_label": "SAFE" if r.label == 0 else "VULNERABLE",
        "confidence": p.confidence,
        "predicted": p.predicted_label,
    })

out = pd.DataFrame(rows)

print("\n=== CONFIDENCE DISTRIBUTION — VALIDATION ===")

print("\nSAFE:")
print(
    out[out.true_label == "SAFE"]["confidence"]
    .describe()
    .to_string()
)

print("\nVULNERABLE:")
print(
    out[out.true_label == "VULNERABLE"]["confidence"]
    .describe()
    .to_string()
)

print("\n=== CONFIDENCE RANGES ===")
print(
    out.groupby("true_label")["confidence"]
    .agg(["min", "max", "mean", "median"])
    .to_string()
)

print("\n=== OVERLAP CHECK ===")

safe_max = out[out.true_label == "SAFE"]["confidence"].max()
vuln_min = out[out.true_label == "VULNERABLE"]["confidence"].min()

print(f"SAFE max confidence       : {safe_max:.4f}")
print(f"Vulnerable min confidence : {vuln_min:.4f}")

if vuln_min > safe_max:
    print("=> Khong co overlap: threshold co kha nang tach SAFE/VULNERABLE.")
else:
    print("=> CO overlap: threshold kho co the tach SAFE/VULNERABLE tot.")
