import json

INPUT_PATH = "../dataset/bandit_scan_raw.json"

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data.get("results", [])
print(f"Tổng số issues Bandit phát hiện: {len(results)}")

# Đếm theo test_id
from collections import Counter
test_id_counter = Counter(r["test_id"] for r in results)

print("\n=== SỐ LƯỢNG THEO test_id (sắp xếp giảm dần) ===")
for test_id, count in test_id_counter.most_common():
    # lấy tên test_name tương ứng (lấy từ issue đầu tiên có test_id đó)
    test_name = next(r["test_name"] for r in results if r["test_id"] == test_id)
    print(f"{test_id} ({test_name}): {count}")