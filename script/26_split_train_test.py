import pandas as pd
from sklearn.model_selection import train_test_split


INPUT_PATH = "../dataset/train_dataset_v1.csv"

TRAIN_OUT = "../dataset/train_split.csv"
VAL_OUT = "../dataset/val_split.csv"
TEST_OUT = "../dataset/test_split.csv"

RANDOM_STATE = 42
TEST_SIZE = 0.15
VAL_SIZE_FROM_REMAINING = 0.15 / 0.85

EXCLUDED_CWES = {"CWE-798"}


df = pd.read_csv(INPUT_PATH)

print(f"Tổng số mẫu ban đầu: {len(df)}")

# CWE-798 được giữ trong dataset nguồn nhưng không dùng cho training/evaluation.
df = df[~df["cwe_id"].isin(EXCLUDED_CWES)].copy()

df["stratify_group"] = (
    df["cwe_id"] + "__" + df["label"].astype(str)
)

print(f"Số mẫu sau khi loại CWE-798: {len(df)}")

# Bước 1: tách Test = 15%
train_val_df, test_df = train_test_split(
    df,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=df["stratify_group"],
)

# Bước 2: từ 85% còn lại, tách Validation sao cho cuối cùng:
# Train = 70%, Validation = 15%, Test = 15%.
train_df, val_df = train_test_split(
    train_val_df,
    test_size=VAL_SIZE_FROM_REMAINING,
    random_state=RANDOM_STATE,
    stratify=train_val_df["stratify_group"],
)

train_df = train_df.drop(columns=["stratify_group"])
val_df = val_df.drop(columns=["stratify_group"])
test_df = test_df.drop(columns=["stratify_group"])

# Lưu các split.
train_df.to_csv(TRAIN_OUT, index=False, encoding="utf-8-sig")
val_df.to_csv(VAL_OUT, index=False, encoding="utf-8-sig")
test_df.to_csv(TEST_OUT, index=False, encoding="utf-8-sig")


print("\n=== KẾT QUẢ SPLIT ===")
print(f"Train      : {len(train_df)} mẫu")
print(f"Validation : {len(val_df)} mẫu")
print(f"Test       : {len(test_df)} mẫu")
print(f"Tổng       : {len(train_df) + len(val_df) + len(test_df)} mẫu")

print("\n=== CWE DISTRIBUTION ===")
print("\nTrain:")
print(train_df["cwe_id"].value_counts().sort_index())

print("\nValidation:")
print(val_df["cwe_id"].value_counts().sort_index())

print("\nTest:")
print(test_df["cwe_id"].value_counts().sort_index())

print("\n=== OUTPUT ===")
print(f"Train      : {TRAIN_OUT}")
print(f"Validation : {VAL_OUT}")
print(f"Test       : {TEST_OUT}")