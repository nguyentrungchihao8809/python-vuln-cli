import pandas as pd

VULN_PATH = "../dataset/bandit_vulnerable_clean.csv"
SAFE_API_PATH = "../dataset/bandit_safe_by_api.csv"
SAFE_COMMENT_PATH = "../dataset/bandit_safe_by_comment.csv"
OUTPUT_PATH = "../dataset/final_bandit.csv"

# --- Vulnerable ---
df_vuln = pd.read_csv(VULN_PATH)
df_vuln_final = pd.DataFrame({
    'source': 'bandit',
    'cwe_id': df_vuln['cwe_id'],
    'label': 1,
    'code': df_vuln['final_code'],
    'origin_ref': df_vuln['filename'].astype(str) + '|line' + df_vuln['line_number'].astype(str)
})

# --- Safe (gộp 2 nguồn, loại trùng theo code) ---
df_safe_api = pd.read_csv(SAFE_API_PATH)
df_safe_comment = pd.read_csv(SAFE_COMMENT_PATH)

df_safe_api_final = pd.DataFrame({
    'source': 'bandit',
    'cwe_id': df_safe_api['cwe_id'],
    'label': 0,
    'code': df_safe_api['code'],
    'origin_ref': df_safe_api['filename'].astype(str) + '|line' + df_safe_api['line_number'].astype(str)
})

df_safe_comment_final = pd.DataFrame({
    'source': 'bandit',
    'cwe_id': df_safe_comment['cwe_id'],
    'label': 0,
    'code': df_safe_comment['code'],
    'origin_ref': df_safe_comment['filename'].astype(str) + '|comment_line' + df_safe_comment['comment_line'].astype(str)
})

df_safe_all = pd.concat([df_safe_comment_final, df_safe_api_final], ignore_index=True)
df_safe_all['code_stripped'] = df_safe_all['code'].fillna('').str.strip()
before_dedup = len(df_safe_all)
df_safe_all = df_safe_all.drop_duplicates(subset=['cwe_id', 'code_stripped'], keep='first')
df_safe_all = df_safe_all.drop(columns=['code_stripped'])
after_dedup = len(df_safe_all)

print(f"Safe trước dedup: {before_dedup}, sau dedup: {after_dedup}")

# --- Gộp toàn bộ ---
df_final = pd.concat([df_vuln_final, df_safe_all], ignore_index=True)
df_final.insert(0, 'sample_id', ['bandit_' + str(i) for i in range(len(df_final))])
df_final['code_lines'] = df_final['code'].fillna('').apply(lambda x: x.count('\n') + 1)
df_final['code_chars'] = df_final['code'].fillna('').apply(len)

print(f"\nTổng số mẫu Bandit cuối cùng: {len(df_final)}")
print("\n=== PHÂN BỐ CHÉO CWE x LABEL ===")
print(pd.crosstab(df_final['cwe_id'], df_final['label']))

df_final.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")