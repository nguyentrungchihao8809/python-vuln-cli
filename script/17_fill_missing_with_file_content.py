import pandas as pd

INPUT_PATH = "../dataset/bandit_vulnerable_functions.csv"
OUTPUT_PATH = "../dataset/bandit_vulnerable_final.csv"
BASE_DIR = "../"

df = pd.read_csv(INPUT_PATH)

final_code = []
final_source_type = []  # "function" hoặc "whole_file"
file_lines_count = []

for _, row in df.iterrows():
    if pd.notnull(row['function_code']):
        final_code.append(row['function_code'])
        final_source_type.append("function")
        file_lines_count.append(None)
    else:
        file_path = BASE_DIR + row['filename'].replace('\\', '/')
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        final_code.append(content)
        final_source_type.append("whole_file")
        file_lines_count.append(content.count('\n') + 1)

df['final_code'] = final_code
df['source_type'] = final_source_type
df['whole_file_lines'] = file_lines_count

print("=== PHÂN LOẠI NGUỒN CODE ===")
print(df['source_type'].value_counts())

print("\n=== THỐNG KÊ ĐỘ DÀI FILE (chỉ với whole_file) ===")
print(df[df['source_type'] == 'whole_file']['whole_file_lines'].describe())

# Cảnh báo file quá lớn (>150 dòng) — có thể không phù hợp làm 1 mẫu
too_large = df[(df['source_type'] == 'whole_file') & (df['whole_file_lines'] > 150)]
print(f"\nSố file quá lớn (>150 dòng): {len(too_large)}")
if len(too_large) > 0:
    print(too_large[['filename', 'whole_file_lines']].drop_duplicates())

df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")