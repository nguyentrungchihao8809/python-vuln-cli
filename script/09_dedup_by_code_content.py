import pandas as pd

INPUT_PATH = "../dataset/dedup_cvefixes.csv"
OUTPUT_PATH = "../dataset/clean_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

before = len(df)

df['code_stripped'] = df['code'].fillna('').str.strip()
df_clean = df.drop_duplicates(subset='code_stripped', keep='first').reset_index(drop=True)
df_clean = df_clean.drop(columns=['code_stripped'])

after = len(df_clean)

print(f"Số dòng trước: {before}")
print(f"Số dòng sau khi loại trùng nội dung code: {after}")
print(f"Đã loại: {before - after} dòng")

print("\n=== PHÂN BỐ CHÉO CWE x LABEL (sau khi làm sạch) ===")
print(pd.crosstab(df_clean['cwe_id'], df_clean['label']))

df_clean.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")