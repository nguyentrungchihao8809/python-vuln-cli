import pandas as pd
from sklearn.model_selection import train_test_split

INPUT_PATH = "../dataset/train_dataset_v1.csv"
TRAIN_OUT = "../dataset/train_split.csv"
TEST_OUT = "../dataset/test_split.csv"

df = pd.read_csv(INPUT_PATH)

train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df['cwe_id']
)

print(f"Tổng số mẫu: {len(df)}")
print(f"Train: {len(train_df)} | Test: {len(test_df)}")

print("\n=== PHÂN BỐ CHÉO CWE x LABEL - TRAIN ===")
print(pd.crosstab(train_df['cwe_id'], train_df['label']))

print("\n=== PHÂN BỐ CHÉO CWE x LABEL - TEST ===")
print(pd.crosstab(test_df['cwe_id'], test_df['label']))

train_df.to_csv(TRAIN_OUT, index=False, encoding='utf-8-sig')
test_df.to_csv(TEST_OUT, index=False, encoding='utf-8-sig')
print(f"\nĐã lưu train tại: {TRAIN_OUT}")
print(f"Đã lưu test tại: {TEST_OUT}")