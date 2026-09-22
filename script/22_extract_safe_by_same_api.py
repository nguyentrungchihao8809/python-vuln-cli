import re
import pandas as pd
import glob
import os

EXAMPLES_DIR = "../bandit-main/examples"
VULN_PATH = "../dataset/bandit_vulnerable_clean.csv"
OUTPUT_PATH = "../dataset/bandit_safe_by_api.csv"

df_vuln = pd.read_csv(VULN_PATH)

def normalize(path):
    path = path.replace('\\', '/')
    idx = path.find("examples/")
    return path[idx:] if idx != -1 else path

df_vuln['filename_norm'] = df_vuln['filename'].apply(normalize)

# API pattern đơn giản: lấy "tên hàm cuối cùng trước dấu (" từ dòng code vulnerable
def extract_api_name(code_line):
    match = re.search(r'([\w\.]+)\s*\(', code_line)
    return match.group(1) if match else None

rows = []

for norm_file, group in df_vuln.groupby('filename_norm'):
    file_path = "../bandit-main/" + norm_file
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    flagged_lines = set(group['line_number'])
    cwe_id = group['cwe_id'].iloc[0]  # giả định 1 file gắn với 1 CWE chính trong nhóm này

    # lấy tập API xuất hiện ở các dòng vulnerable
    apis = set()
    for ln in flagged_lines:
        if ln - 1 < len(lines):
            api = extract_api_name(lines[ln - 1])
            if api:
                apis.add(api)

    # quét toàn bộ file, tìm dòng dùng cùng API nhưng KHÔNG bị flag
    for i, line in enumerate(lines, start=1):
        if i in flagged_lines:
            continue
        api = extract_api_name(line)
        if api in apis:
            rows.append({
                "filename": norm_file,
                "cwe_id": cwe_id,
                "line_number": i,
                "matched_api": api,
                "code": line.rstrip()
            })

df_safe = pd.DataFrame(rows)
print(f"Tổng số mẫu safe trích được (theo cùng API): {len(df_safe)}")
if len(df_safe) > 0:
    print("\n=== PHÂN BỐ THEO CWE ===")
    print(df_safe['cwe_id'].value_counts())
    print("\n=== VÍ DỤ 5 MẪU ===")
    for _, row in df_safe.head(5).iterrows():
        print(f"\n--- {row['filename']} | {row['cwe_id']} | line {row['line_number']} | api={row['matched_api']} ---")
        print(row['code'])

df_safe.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")