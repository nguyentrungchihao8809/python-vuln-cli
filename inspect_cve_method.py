import sqlite3
from pathlib import Path

db = Path(__file__).parent / "CVEfixes.db"
conn = sqlite3.connect(
    f"file:{db.resolve().as_posix()}?mode=ro",
    uri=True,
)

try:
    cur = conn.cursor()

    file_change_id = "217785133698176"

    cur.execute("""
        SELECT
            method_change_id,
            name,
            signature,
            start_line,
            end_line,
            before_change,
            code
        FROM method_change
        WHERE file_change_id = ?
    """, (file_change_id,))

    rows = cur.fetchmany(10)
    print(f"=== METHODS FOUND (maximum 10): {len(rows)} ===")

    for row in rows:
        method_id, name, signature, start, end, before, code = row

        print("\n" + "=" * 50)
        print(f"METHOD: {name}")
        print(f"SIGNATURE: {signature}")
        print(f"LINES: {start}-{end}")
        print("\n[BEFORE_CHANGE]")
        print((before or "")[:2000])
        print("\n[CODE]")
        print((code or "")[:2000])

finally:
    conn.close()