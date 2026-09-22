import ast
import pandas as pd

INPUT_PATH = "../dataset/bandit_vulnerable_raw.csv"
OUTPUT_PATH = "../dataset/bandit_vulnerable_functions.csv"
BASE_DIR = "../"  # vì filename trong CSV là đường dẫn dạng "bandit-main/examples\..."

def find_enclosing_function(file_path, line_number):
    """Trả về (function_name, source_code) của hàm chứa line_number, hoặc (None, None) nếu không có (code ở module-level)."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()
        tree = ast.parse(source)
    except Exception as e:
        return None, None, f"PARSE_ERROR: {e}"

    best_match = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = node.lineno
            end = max(
                getattr(child, 'end_lineno', start)
                for child in ast.walk(node)
            ) if hasattr(node, 'end_lineno') else start
            end = max(end, getattr(node, 'end_lineno', start))
            if start <= line_number <= end:
                # ưu tiên hàm nhỏ nhất bao quanh (trường hợp hàm lồng nhau)
                if best_match is None or (end - start) < (best_match[2] - best_match[1]):
                    best_match = (node, start, end)

    if best_match is None:
        return None, None, None

    node, start, end = best_match
    func_source = ast.get_source_segment(source, node)
    return node.name, func_source, None

df = pd.read_csv(INPUT_PATH)

func_names = []
func_codes = []
errors = []

for _, row in df.iterrows():
    file_path = BASE_DIR + row['filename'].replace('\\', '/')
    fname, fcode, err = find_enclosing_function(file_path, row['line_number'])
    func_names.append(fname)
    func_codes.append(fcode)
    errors.append(err)

df['function_name'] = func_names
df['function_code'] = func_codes
df['extract_error'] = errors

print(f"Tổng số dòng: {len(df)}")
print(f"Số dòng KHÔNG tìm được hàm bao quanh (module-level code): {df['function_code'].isnull().sum()}")
print(f"Số dòng bị lỗi parse: {df['extract_error'].notnull().sum()}")

df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu tại: {OUTPUT_PATH}")