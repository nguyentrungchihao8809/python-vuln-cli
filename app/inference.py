import os
import re
import ast
import json
import sys
import subprocess
import tempfile
import numpy as np

import torch
import torch.nn.functional as F
import joblib
import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from schemas import CodeSnippetRequest, ScanResponse, DetectionResult

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "..", "models")
CODEBERT_DIR_LOCAL = os.path.join(MODELS_DIR, "codebert_finetuned")
HF_MODEL_ID = "haoday333/python-vuln-codebert"

# Uu tien model local (neu co) de dev nhanh; neu khong co thi tai tu Hugging Face Hub (dung cho CI/CD)
_model_source = CODEBERT_DIR_LOCAL if os.path.exists(CODEBERT_DIR_LOCAL) else HF_MODEL_ID

print(f"Dang load CodeBERT model tu: {_model_source}")
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
_model = AutoModelForSequenceClassification.from_pretrained(_model_source).to(_device)
_tokenizer = AutoTokenizer.from_pretrained(_model_source)

# label_encoder van uu tien local; neu khong co (CI), dung danh sach nhan co dinh da biet
LABEL_ENCODER_PATH = os.path.join(MODELS_DIR, "label_encoder.pkl")
if os.path.exists(LABEL_ENCODER_PATH):
    _label_encoder = joblib.load(LABEL_ENCODER_PATH)
else:
    from sklearn.preprocessing import LabelEncoder
    _label_encoder = LabelEncoder()
    _label_encoder.classes_ = np.array(['CWE-22', 'CWE-78', 'CWE-79', 'CWE-798', 'CWE-89', 'SAFE'])

_model.eval()
print(f"Da load xong. Dang chay tren: {_device}")


# ============ TIER 1: BANDIT (RULE-BASED) ============
BANDIT_CWE_MAPPING = {
    "B608": "CWE-89", "B610": "CWE-89", "B611": "CWE-89",
    "B105": "CWE-798", "B106": "CWE-798", "B107": "CWE-798",
    "B602": "CWE-78", "B603": "CWE-78", "B604": "CWE-78",
    "B605": "CWE-78", "B606": "CWE-78", "B607": "CWE-78", "B609": "CWE-78",
    "B703": "CWE-79", "B704": "CWE-79", "B701": "CWE-79", "B702": "CWE-79",
}


def tier1_predict(code: str) -> DetectionResult:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(code)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-f", "json", tmp_path],
            capture_output=True, text=True, timeout=10
        )
        output = json.loads(result.stdout) if result.stdout else {"results": []}
    except Exception:
        output = {"results": []}
    finally:
        os.remove(tmp_path)

    issues = output.get("results", [])
    relevant = [i for i in issues if i["test_id"] in BANDIT_CWE_MAPPING]

    if not relevant:
        return DetectionResult(source="bandit", predicted_label="SAFE", confidence=None)

    return DetectionResult(
        source="bandit",
        predicted_label=BANDIT_CWE_MAPPING[relevant[0]["test_id"]],
        confidence=None
    )


# ============ TIER 2: CODEBERT (ML) ============
def tier2_predict(code: str, max_len: int = 512) -> DetectionResult:
    inputs = _tokenizer(
        code, truncation=True, max_length=max_len,
        padding="max_length", return_tensors="pt"
    ).to(_device)

    with torch.no_grad():
        outputs = _model(**inputs)
        proba = F.softmax(outputs.logits, dim=1).cpu().numpy()[0]

    pred_idx = proba.argmax()
    pred_label = _label_encoder.inverse_transform([pred_idx])[0]
    confidence = float(proba[pred_idx])

    return DetectionResult(source="codebert", predicted_label=pred_label, confidence=confidence)


# ============ HAM CHINH THUC: NHAN CodeSnippetRequest, TRA VE ScanResponse ============
def scan_code(request: CodeSnippetRequest) -> ScanResponse:
    tier1_result = tier1_predict(request.code)

    # Neu Bandit phat hien (khong phai SAFE) -> tin theo Bandit (FPR thap, dang tin cay khi "len tieng")
    if tier1_result.predicted_label != "SAFE":
        final_label = tier1_result.predicted_label
        detections = [tier1_result]
    else:
        # Bandit im lang -> chay CodeBERT de bat cac truong hop Bandit bo sot
        tier2_result = tier2_predict(request.code)
        final_label = tier2_result.predicted_label
        detections = [tier1_result, tier2_result]

    return ScanResponse(
        request=request,
        final_label=final_label,
        is_vulnerable=(final_label != "SAFE"),
        detections=detections
    )


if __name__ == "__main__":
    test_request = CodeSnippetRequest(
        code="import os\ndef run(cmd):\n    os.system(cmd)",
        file_path="test.py"
    )
    response = scan_code(test_request)
    print(response.model_dump_json(indent=2))