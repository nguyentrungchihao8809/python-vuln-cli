import json
import pandas as pd

INPUT_PATH = "../dataset/bandit_scan_raw.json"
OUTPUT_PATH = "../dataset/bandit_vulnerable_raw.csv"

# Mapping test_id -> CWE mục tiêu
CWE_MAPPING = {
    "B608": "CWE-89", "B610": "CWE-89", "B611": "CWE-89",
    "B105": "CWE-798", "B106": "CWE-798", "B107": "CWE-798",
    "B602": "CWE-78", "B603": "CWE-78", "B604": "CWE-78",
    "B605": "CWE-78", "B606": "CWE-78", "B607": "CWE-78", "B609": "CWE-78",
    "B703": "CWE-79", "B704": "CWE-79", "B701": "CWE-79", "B702": "CWE-79",
}

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data.get("results", [])

rows = []
for r in results:
    test_id = r["test_id"]
    if test_id not in CWE_MAPPING:
        continue
    rows.append({
        "test_id": test_id,
        "cwe_id": CWE_MAPPING[test_id],
        "filename": r["filename"],
        "line_number": r["line_number"],
        "code": r["code"],
        "issue_severity": r["issue_severity"],
        "issue_confidence": r["issue_confidence"],
    })

df = pd.DataFrame(rows)
print(f"Tổng số mẫu vulnerable trích được: {len(df)}")
print("\n=== PHÂN BỐ THEO CWE ===")
print(df['cwe_id'].value_counts())

df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")