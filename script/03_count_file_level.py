import sqlite3

DB_PATH = "../CVEfixes.db"

TARGET_CWES = ['CWE-89', 'CWE-798', 'CWE-22', 'CWE-78', 'CWE-79']

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

placeholder = ','.join(['?'] * len(TARGET_CWES))

query = f"""
SELECT cc.cwe_id, COUNT(DISTINCT fc.file_change_id) as num_files
FROM cwe_classification cc
JOIN fixes f ON cc.cve_id = f.cve_id
JOIN file_change fc ON f.hash = fc.hash
WHERE cc.cwe_id IN ({placeholder})
  AND fc.programming_language = 'Python'
GROUP BY cc.cwe_id
ORDER BY num_files DESC;
"""

cursor.execute(query, TARGET_CWES)
rows = cursor.fetchall()

print("=== SỐ LƯỢNG FILE_CHANGE THEO CWE (chỉ Python, trước khi tách method) ===")
total = 0
for cwe_id, count in rows:
    print(f"{cwe_id}: {count}")
    total += count
print(f"\nTổng: {total}")

conn.close()