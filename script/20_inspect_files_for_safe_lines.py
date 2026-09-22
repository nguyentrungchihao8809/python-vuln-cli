import pandas as pd

INPUT_PATH = "../dataset/bandit_vulnerable_clean.csv"
BASE_DIR = "../"

df = pd.read_csv(INPUT_PATH)

# Lấy danh sách file duy nhất kèm CWE tương ứng và các dòng đã bị flag
file_cwe_lines = df.groupby(['filename', 'cwe_id'])['line_number'].apply(list).reset_index()

for _, row in file_cwe_lines.iterrows():
    file_path = BASE_DIR + row['filename'].replace('\\', '/')
    flagged_lines = set(row['line_number'])

    print(f"\n{'='*80}")
    print(f"FILE: {row['filename']} | CWE: {row['cwe_id']} | Dòng bị flag: {sorted(flagged_lines)}")
    print('='*80)

    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    for i, line in enumerate(lines, start=1):
        marker = ">>> VULNERABLE" if i in flagged_lines else "               "
        print(f"{i:4d} {marker} | {line.rstrip()}")