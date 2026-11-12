import sys
sys.path.insert(0, r".\app")

import pandas as pd
from inference import tier2_predict


df = pd.read_csv(r".\dataset\val_split.csv")

rows = []

for r in df.itertuples():
    result = tier2_predict(r.code)

    rows.append({
        "true_label": "SAFE" if r.label == 0 else r.cwe_id,
        "pred_label": result.predicted_label,
        "confidence": result.confidence,
    })

out = pd.DataFrame(rows)

print("\n=== THRESHOLD SCAN — VALIDATION ===")
print(
    "Threshold | Vuln Recall | SAFE->Vuln FPR | "
    "Vuln->SAFE FNR | Accuracy"
)
print("-" * 70)

total_vuln = (out["true_label"] != "SAFE").sum()
total_safe = (out["true_label"] == "SAFE").sum()

for threshold in [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90]:

    final_pred = out["pred_label"].where(
        (out["pred_label"] == "SAFE") |
        (out["confidence"] >= threshold),
        "SAFE"
    )

    vuln_recall = (
        ((out["true_label"] != "SAFE") &
         (final_pred != "SAFE")).sum()
        / total_vuln
    )

    safe_fpr = (
        ((out["true_label"] == "SAFE") &
         (final_pred != "SAFE")).sum()
        / total_safe
    )

    vuln_fnr = 1 - vuln_recall

    accuracy = (out["true_label"] == final_pred).mean()

    print(
        f"{threshold:.2f}       | "
        f"{vuln_recall:.4f}      | "
        f"{safe_fpr:.4f}        | "
        f"{vuln_fnr:.4f}        | "
        f"{accuracy:.4f}"
    )
