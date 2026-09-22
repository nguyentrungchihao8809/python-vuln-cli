import sqlite3

DB_PATH = "../CVEfixes.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT before_change FROM method_change;")
rows = cursor.fetchall()

print("=== CÁC GIÁ TRỊ DUY NHẤT CỦA before_change ===")
for r in rows:
    print(r)

# Đếm số lượng theo từng giá trị
cursor.execute("""
    SELECT before_change, COUNT(*) 
    FROM method_change 
    GROUP BY before_change;
""")
rows2 = cursor.fetchall()
print("\n=== SỐ LƯỢNG THEO GIÁ TRỊ ===")
for r in rows2:
    print(r)

conn.close()