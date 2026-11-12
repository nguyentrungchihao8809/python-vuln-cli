import os
import sys
import json
import time
import pandas as pd

from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(ROOT_DIR, "app")

if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from inference import tier1_predict, tier2_predict, scan_code
from schemas import CodeSnippetRequest


TEST_PATH = os.path.join(ROOT_DIR, "dataset", "test_split.csv")
OUTPUT_DIR = os.path.join(ROOT_DIR, "evaluation_results")

LABELS = [
    "CWE-22",
    "CWE-78",
    "CWE-79",
    "CWE-89",
    "SAFE",
]


def build_ground_truth(row):
    if int(row["label"]) == 0:
        return "SAFE"

    cwe = str(row["cwe_id"])
    if cwe not in LABELS:
        raise ValueError(f"CWE khong hop le: {cwe}")

    return cwe


def evaluate_model(name, y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)

    precision, recall, f1, support = precision_recall_fscore_support(
        y_true,
        y_pred,
        labels=LABELS,
        zero_division=0,
    )

    macro_f1 = f1.mean()
    weighted_f1 = (
        (f1 * support).sum() / support.sum()
        if support.sum() > 0
        else 0.0
    )

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=LABELS,
    )

    # SAFE FPR:
    # FP_SAFE / (FP_SAFE + TN_SAFE)
    # Positive = SAFE
    safe_idx = LABELS.index("SAFE")
    safe_tp = cm[safe_idx, safe_idx]
    safe_fp = cm[:, safe_idx].sum() - safe_tp
    safe_fn = cm[safe_idx, :].sum() - safe_tp
    safe_tn = cm.sum() - safe_tp - safe_fp - safe_fn

    vulnerability_fnr = (
        safe_fp / (safe_fp + safe_tn)
        if (safe_fp + safe_tn) > 0
        else 0.0
    )

    # Binary vulnerability errors.
    true_vulnerable = [x != "SAFE" for x in y_true]
    pred_vulnerable = [x != "SAFE" for x in y_pred]

    vulnerable_to_safe = sum(
        t and not p
        for t, p in zip(true_vulnerable, pred_vulnerable)
    )

    safe_to_vulnerable = sum(
        not t and p
        for t, p in zip(true_vulnerable, pred_vulnerable)
    )

    print(
    f"[DEBUG] {name}: "
    f"len_true={len(y_true)}, "
    f"len_pred={len(y_pred)}, "
    f"vuln_to_safe={vulnerable_to_safe}, "
    f"safe_to_vuln={safe_to_vulnerable}, "
    f"vulnerability_fnr={vulnerability_fnr}"
)

    report = classification_report(
        y_true,
        y_pred,
        labels=LABELS,
        target_names=LABELS,
        zero_division=0,
        output_dict=True,
    )

    result = {
        "model": name,
        "n_samples": len(y_true),
        "accuracy": float(accuracy),
        "macro_f1": float(macro_f1),
        "weighted_f1": float(weighted_f1),
        "vulnerability_fnr": float(vulnerability_fnr),
        "vulnerable_to_safe_fn": int(vulnerable_to_safe),
        "safe_to_vulnerable_fp": int(safe_to_vulnerable),
        "per_class": {},
        "confusion_matrix": cm.tolist(),
        "confusion_matrix_labels": LABELS,
        "classification_report": report,
    }

    for label, p, r, f, s in zip(
        LABELS,
        precision,
        recall,
        f1,
        support,
    ):
        result["per_class"][label] = {
            "precision": float(p),
            "recall": float(r),
            "f1": float(f),
            "support": int(s),
        }

    return result


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 80)
    print("MODEL EVALUATION - SAME TEST SET")
    print("=" * 80)

    df = pd.read_csv(TEST_PATH)

    print(f"Test file : {TEST_PATH}")
    print(f"Test shape: {df.shape}")

    if len(df) != 84:
        raise ValueError(
            f"Test set phai co 84 mau, nhung hien tai co {len(df)} mau."
        )

    required_columns = {
        "sample_id",
        "cwe_id",
        "label",
        "code",
    }

    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Thieu cot: {sorted(missing)}")

    y_true = [build_ground_truth(row) for _, row in df.iterrows()]

    print("\n=== GROUND TRUTH ===")
    print(pd.Series(y_true).value_counts().reindex(LABELS, fill_value=0))

    predictions = {
        "Bandit-only": [],
        "CodeBERT-only": [],
        "Cascading": [],
    }

    rows = []

    for index, row in df.iterrows():
        sample_id = row["sample_id"]
        code = row["code"]
        true_label = y_true[index]

        print(
            f"\rDang danh gia: {index + 1:02d}/84 | {sample_id}",
            end="",
            flush=True,
        )

        bandit = tier1_predict(code)
        codebert = tier2_predict(code)
        cascading = scan_code(
            CodeSnippetRequest(code=code, file_path=f"test_{sample_id}.py", function_name="test_func", start_line=1)
        )

        predictions["Bandit-only"].append(
            bandit.predicted_label
        )

        predictions["CodeBERT-only"].append(
            codebert.predicted_label
        )

        predictions["Cascading"].append(
            cascading.final_label
        )

        rows.append({
            "sample_id": sample_id,
            "true_label": true_label,
            "bandit_pred": bandit.predicted_label,
            "codebert_pred": codebert.predicted_label,
            "cascading_pred": cascading.final_label,
            "codebert_confidence": codebert.confidence,
        })

    print("\n")

    all_results = {}

    for name in [
        "Bandit-only",
        "CodeBERT-only",
        "Cascading",
    ]:
        all_results[name] = evaluate_model(
            name,
            y_true,
            predictions[name],
        )

    prediction_df = pd.DataFrame(rows)

    prediction_path = os.path.join(
        OUTPUT_DIR,
        "predictions_84.csv",
    )
    prediction_df.to_csv(
        prediction_path,
        index=False,
        encoding="utf-8-sig",
    )

    results_path = os.path.join(
        OUTPUT_DIR,
        "evaluation_results.json",
    )

    with open(
        results_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            all_results,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    summary_rows = []

    for name, result in all_results.items():
        summary_rows.append({
            "Model": name,
            "Accuracy": result["accuracy"],
            "Macro-F1": result["macro_f1"],
            "Weighted-F1": result["weighted_f1"],
            "Vulnerability-FNR": result["vulnerability_fnr"],
            "Vuln->SAFE": result["vulnerable_to_safe_fn"],
            "SAFE->Vuln": result["safe_to_vulnerable_fp"],
        })

    summary_df = pd.DataFrame(summary_rows)

    print(
        summary_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    print("\n" + "=" * 80)
    print("PER-CLASS F1")
    print("=" * 80)

    for name, result in all_results.items():
        print(f"\n{name}")
        for label in LABELS:
            data = result["per_class"][label]
            print(
                f"  {label:7s} "
                f"P={data['precision']:.4f} "
                f"R={data['recall']:.4f} "
                f"F1={data['f1']:.4f} "
                f"Support={data['support']}"
            )

    print("\n" + "=" * 80)
    print("CONFUSION MATRICES")
    print("Rows = True | Columns = Predicted")
    print(f"Labels = {LABELS}")
    print("=" * 80)

    for name, result in all_results.items():
        print(f"\n{name}")
        print(
            pd.DataFrame(
                result["confusion_matrix"],
                index=LABELS,
                columns=LABELS,
            )
        )

    print("\n" + "=" * 80)
    print("OUTPUT FILES")
    print("=" * 80)
    print(prediction_path)
    print(results_path)


if __name__ == "__main__":
    main()
