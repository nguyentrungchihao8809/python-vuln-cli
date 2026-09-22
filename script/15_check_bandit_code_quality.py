import pandas as pd

INPUT_PATH = "../dataset/bandit_vulnerable_raw.csv"

df = pd.read_csv(INPUT_PATH)

df['code_stripped'] = df['code'].fillna('').str.strip()
df['code_lines'] = df['code_stripped'].apply(lambda x: x.count('\n') + 1)
df['code_chars'] = df['code_stripped'].apply(len)

print("=== THỐNG KÊ ĐỘ DÀI CODE CONTEXT (số dòng) ===")
print(df['code_lines'].describe())

print("\n=== THỐNG KÊ ĐỘ DÀI CODE CONTEXT (ký tự) ===")
print(df['code_chars'].describe())

dup_count = df.duplicated(subset='code_stripped').sum()
print(f"\nSố dòng trùng nội dung code y hệt: {dup_count}")

print("\n=== VÍ DỤ 3 CODE SNIPPET NGẪU NHIÊN ===")
for i, row in df.sample(3, random_state=42).iterrows():
    print(f"\n--- {row['cwe_id']} | {row['filename']} | line {row['line_number']} ---")
    print(row['code'])