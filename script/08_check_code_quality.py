import pandas as pd

INPUT_PATH = "../dataset/dedup_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

print(f"Tổng số dòng: {len(df)}")

# Kiểm tra null/rỗng
null_code = df['code'].isnull().sum()
empty_code = (df['code'].fillna('').str.strip() == '').sum()
print(f"\nSố dòng code = null: {null_code}")
print(f"Số dòng code rỗng (chuỗi trắng): {empty_code}")

# Kiểm tra code trùng nội dung y hệt
df['code_stripped'] = df['code'].fillna('').str.strip()
dup_code_count = df.duplicated(subset='code_stripped').sum()
print(f"\nSố dòng có nội dung code trùng y hệt dòng khác: {dup_code_count}")

# Phân bố độ dài code (theo số ký tự và số dòng)
df['code_len_chars'] = df['code_stripped'].apply(len)
df['code_len_lines'] = df['code_stripped'].apply(lambda x: x.count('\n') + 1)

print("\n=== THỐNG KÊ ĐỘ DÀI CODE (ký tự) ===")
print(df['code_len_chars'].describe())

print("\n=== THỐNG KÊ ĐỘ DÀI CODE (số dòng) ===")
print(df['code_len_lines'].describe())

# Cảnh báo code quá ngắn (khả năng bị cắt lỗi khi extract)
too_short = (df['code_len_chars'] < 20).sum()
print(f"\nSố dòng code quá ngắn (<20 ký tự): {too_short}")