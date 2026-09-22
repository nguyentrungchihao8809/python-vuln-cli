import pandas as pd

INPUT_PATH = "../dataset/bandit_vulnerable_final.csv"
OUTPUT_PATH = "../dataset/bandit_vulnerable_clean.csv"

df = pd.read_csv(INPUT_PATH)

before = len(df)

# Loại trùng theo (cwe_id, final_code) - vì 1 file có thể liên quan >1 CWE khác nhau nên vẫn giữ
df_dedup = df.drop_duplicates(subset=['cwe_id', 'final_code'], keep='first').reset_index(drop=True)

after = len(df_dedup)

print(f"Số dòng trước khi loại trùng: {before}")
print(f"Số dòng sau khi loại trùng: {after}")
print(f"Đã loại: {before - after} dòng")

print("\n=== PHÂN BỐ THEO CWE (sau dedup) ===")
print(df_dedup['cwe_id'].value_counts())

print("\n=== PHÂN BỐ THEO source_type ===")
print(df_dedup['source_type'].value_counts())

df_dedup.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")