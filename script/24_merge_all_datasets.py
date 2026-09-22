import pandas as pd

CVEFIXES_PATH = "../dataset/final_cvefixes.csv"
BANDIT_PATH = "../dataset/final_bandit.csv"
OUTPUT_PATH = "../dataset/train_dataset_v1.csv"

df_cve = pd.read_csv(CVEFIXES_PATH)
df_bandit = pd.read_csv(BANDIT_PATH)

# Đồng bộ cột chung
common_cols = ['sample_id', 'source', 'cwe_id', 'label', 'code', 'code_lines', 'code_chars', 'origin_ref']
df_cve = df_cve[common_cols]
df_bandit = df_bandit[common_cols]

df_merged = pd.concat([df_cve, df_bandit], ignore_index=True)

# Kiểm tra trùng code giữa 2 nguồn
df_merged['code_stripped'] = df_merged['code'].fillna('').str.strip()
dup_cross_source = df_merged.duplicated(subset='code_stripped', keep=False).sum()
print(f"Số dòng code trùng nhau (kể cả trùng nội bộ 1 nguồn): {dup_cross_source}")

before = len(df_merged)
df_merged = df_merged.drop_duplicates(subset='code_stripped', keep='first').reset_index(drop=True)
after = len(df_merged)
print(f"Trước loại trùng cuối: {before}, sau: {after}")

df_merged = df_merged.drop(columns=['code_stripped'])

print(f"\n=== TỔNG QUAN DATASET CUỐI CÙNG ===")
print(f"Tổng số mẫu: {len(df_merged)}")
print("\n=== PHÂN BỐ THEO SOURCE ===")
print(df_merged['source'].value_counts())
print("\n=== PHÂN BỐ CHÉO CWE x LABEL ===")
print(pd.crosstab(df_merged['cwe_id'], df_merged['label']))

df_merged.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")