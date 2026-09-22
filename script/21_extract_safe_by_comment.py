import re
import pandas as pd
import glob
import os

EXAMPLES_DIR = "../bandit-main/examples"
VULN_PATH = "../dataset/bandit_vulnerable_clean.csv"
OUTPUT_PATH = "../dataset/bandit_safe_by_comment.csv"

SAFE_KEYWORDS = re.compile(r"#.*(okay|ok:|not vulnerable|safe)", re.IGNORECASE)

df_vuln = pd.read_csv(VULN_PATH)

def normalize(path):
    path = path.replace('\\', '/')
    idx = path.find("examples/")
    return path[idx:] if idx != -1 else path

# map filename (normalized) -> set các cwe_id đã biết liên quan tới file đó (từ vulnerable set)
df_vuln['filename_norm'] = df_vuln['filename'].apply(normalize)
file_to_cwes = df_vuln.groupby('filename_norm')['cwe_id'].apply(set).to_dict()

all_py_files = glob.glob(os.path.join(EXAMPLES_DIR, "**", "*.py"), recursive=True)

rows = []
for file_path in all_py_files:
    norm = normalize(file_path.replace('\\', '/'))
    if norm not in file_to_cwes:
        continue  # chỉ xét file có liên quan tới CWE mục tiêu

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    flagged_lines = set(df_vuln[df_vuln['filename_norm'] == norm]['line_number'])

    for i in range(len(lines)):
        if SAFE_KEYWORDS.search(lines[i]):
            # lấy các dòng code NGAY SAU dòng comment (tối đa 5 dòng, dừng khi gặp dòng trống)
            code_lines = []
            for j in range(i + 1, min(i + 6, len(lines))):
                if lines[j].strip() == "":
                    break
                if (j + 1) in flagged_lines:
                    break
                code_lines.append(lines[j].rstrip())
            if code_lines:
                for cwe in file_to_cwes[norm]:
                    rows.append({
                        "filename": norm,
                        "cwe_id": cwe,
                        "comment_line": i + 1,
                        "code": "\n".join(code_lines)
                    })

df_safe = pd.DataFrame(rows)
print(f"Tổng số mẫu safe trích được (theo comment): {len(df_safe)}")
if len(df_safe) > 0:
    print("\n=== PHÂN BỐ THEO CWE ===")
    print(df_safe['cwe_id'].value_counts())
    print("\n=== VÍ DỤ 3 MẪU ===")
    for _, row in df_safe.head(3).iterrows():
        print(f"\n--- {row['filename']} | {row['cwe_id']} | dòng comment {row['comment_line']} ---")
        print(row['code'])

df_safe.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")