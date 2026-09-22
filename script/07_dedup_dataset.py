import pandas as pd

INPUT_PATH = "../dataset/raw_cvefixes.csv"
OUTPUT_PATH = "../dataset/dedup_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

before = len(df)

# Giữ dòng đầu tiên cho mỗi method_change_id (loại các dòng trùng phía sau)
df_dedup = df.drop_duplicates(subset='method_change_id', keep='first').reset_index(drop=True)

after = len(df_dedup)

print(f"Số dòng trước khi loại trùng: {before}")
print(f"Số dòng sau khi loại trùng: {after}")
print(f"Đã loại: {before - after} dòng")

print("\n=== PHÂN BỐ THEO CWE (sau dedup) ===")
print(df_dedup['cwe_id'].value_counts())

print("\n=== PHÂN BỐ THEO LABEL (sau dedup) ===")
print(df_dedup['label'].value_counts())

print("\n=== PHÂN BỐ CHÉO CWE x LABEL ===")
print(pd.crosstab(df_dedup['cwe_id'], df_dedup['label']))

df_dedup.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")