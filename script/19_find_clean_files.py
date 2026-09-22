import json
import glob
import os

INPUT_PATH = "../dataset/bandit_scan_raw.json"
EXAMPLES_DIR = "../bandit-main/examples"

def normalize(path):
    path = path.replace('\\', '/')
    # chỉ giữ phần từ "examples/" trở đi
    idx = path.find("examples/")
    return path[idx:] if idx != -1 else path

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

results = data.get("results", [])
flagged_files = set(normalize(r["filename"]) for r in results)

all_py_files = glob.glob(os.path.join(EXAMPLES_DIR, "**", "*.py"), recursive=True)
all_py_files_norm = [normalize(f) for f in all_py_files]

clean_files = [f for f in all_py_files_norm if f not in flagged_files]

print(f"Tổng số file .py trong examples: {len(all_py_files_norm)}")
print(f"Số file bị Bandit flag (có ít nhất 1 issue): {len(flagged_files)}")
print(f"Số file hoàn toàn sạch (candidate cho safe): {len(clean_files)}")

print("\n=== DANH SÁCH FILE SẠCH ===")
for f in clean_files:
    print(f)