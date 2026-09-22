import pandas as pd

INPUT_PATH = "../dataset/clean_cvefixes.csv"
OUTPUT_PATH = "../dataset/final_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

df_final = pd.DataFrame({
    'sample_id': ['cvefixes_' + str(i) for i in range(len(df))],
    'source': 'cvefixes',
    'cwe_id': df['cwe_id'],
    'label': df['label'],
    'code': df['code'],
    'code_lines': df['code'].fillna('').apply(lambda x: x.count('\n') + 1),
    'code_chars': df['code'].fillna('').apply(len),
    'origin_ref': df['cve_id'].astype(str) + '|' + df['method_change_id'].astype(str)
})

print("=== SCHEMA CUỐI CÙNG ===")
print(df_final.dtypes)
print(f"\nTổng số mẫu: {len(df_final)}")
print("\n=== 3 DÒNG ĐẦU ===")
print(df_final.head(3).to_string())

df_final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")