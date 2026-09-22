import sqlite3

DB_PATH = "../CVEfixes.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Lấy danh sách tất cả bảng
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=== DANH SÁCH BẢNG ===")
for t in tables:
    print(t[0])

print("\n=== CHI TIẾT TỪNG BẢNG ===")
for t in tables:
    table_name = t[0]
    print(f"\n--- Bảng: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    print(f"  => Số dòng: {count}")

conn.close()