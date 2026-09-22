import pandas as pd

INPUT_PATH = "../dataset/raw_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

dup_ids = df[df.duplicated('method_change_id', keep=False)]['method_change_id'].unique()

print(f"Số method_change_id bị trùng: {len(dup_ids)}")
print("\n=== VÍ DỤ 5 NHÓM TRÙNG ĐẦU TIÊN ===")

for mid in dup_ids[:5]:
    sub = df[df['method_change_id'] == mid]
    print(f"\n--- method_change_id: {mid} ---")
    print(sub[['cve_id', 'cwe_id', 'label', 'method_name']].to_string(index=False))