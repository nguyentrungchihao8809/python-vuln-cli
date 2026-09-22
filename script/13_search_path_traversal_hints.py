import json

INPUT_PATH = "../dataset/bandit_scan_raw.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data.get("results", [])

keywords = ["path", "traversal", "directory", "../", "zip", "tar"]

print("=== CÁC ISSUE CÓ LIÊN QUAN TỪ KHÓA PATH/TRAVERSAL ===")
found = []
for r in results:
    text = (r.get("issue_text", "") + " " + r.get("test_name", "")).lower()
    if any(kw in text for kw in keywords):
        found.append(r)
        print(f"{r['test_id']} ({r['test_name']}) - {r['filename']} - line {r['line_number']}")
        print(f"   -> {r['issue_text'][:100]}")

print(f"\nTổng số issue liên quan: {len(found)}")