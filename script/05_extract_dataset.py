import sqlite3
import pandas as pd

DB_PATH = "../CVEfixes.db"
OUTPUT_PATH = "../dataset/raw_cvefixes.csv"

TARGET_CWES = ['CWE-89', 'CWE-22', 'CWE-78', 'CWE-79']

conn = sqlite3.connect(DB_PATH)

placeholder = ','.join(['?'] * len(TARGET_CWES))

query = f"""
SELECT 
    mc.method_change_id,
    fc.file_change_id,
    f.cve_id,
    cc.cwe_id,
    mc.name AS method_name,
    mc.code,
    mc.before_change,
    fc.old_path,
    fc.new_path
FROM cwe_classification cc
JOIN fixes f ON cc.cve_id = f.cve_id
JOIN file_change fc ON f.hash = fc.hash
JOIN method_change mc ON fc.file_change_id = mc.file_change_id
WHERE cc.cwe_id IN ({placeholder})
  AND fc.programming_language = 'Python';
"""

df = pd.read_sql_query(query, conn, params=TARGET_CWES)
conn.close()

# Gán nhãn: before_change = True -> vulnerable (1), False -> safe (0)
df['label'] = df['before_change'].apply(lambda x: 1 if x == 'True' else 0)

print("=== TỔNG QUAN DATASET THÔ ===")
print(f"Tổng số dòng: {len(df)}")
print("\nPhân bố theo CWE:")
print(df['cwe_id'].value_counts())
print("\nPhân bố theo label (1=vulnerable, 0=safe):")
print(df['label'].value_counts())
print("\nSố dòng trùng lặp (method_change_id):", df['method_change_id'].duplicated().sum())

df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")