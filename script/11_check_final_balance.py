import pandas as pd

INPUT_PATH = "../dataset/final_cvefixes.csv"

df = pd.read_csv(INPUT_PATH)

print("=== PHÂN BỐ LABEL TOÀN BỘ ===")
print(df['label'].value_counts())

print("\n=== PHÂN BỐ CHÉO CWE x LABEL ===")
print(pd.crosstab(df['cwe_id'], df['label']))