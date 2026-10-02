import sys
from pathlib import Path

import numpy as np


APP_DIR = Path(__file__).resolve().parent.parent / "app"
sys.path.insert(0, str(APP_DIR))

import inference  # noqa: E402


def test_temperature_loaded_from_calibration():
    assert np.isclose(
        inference.TEMPERATURE,
        1.627714614648346,
        rtol=0,
        atol=1e-12,
    )


def test_calibration_has_five_classes():
    assert inference._calibration["num_classes"] == 5


def test_label_mapping_matches_model():
    assert list(inference._label_encoder.classes_) == [
        "CWE-22",
        "CWE-78",
        "CWE-79",
        "CWE-89",
        "SAFE",
    ]

def test_temperature_scaling_formula():
    import torch

    logits = torch.tensor([[2.0, 1.0, 0.0, -1.0, -2.0]])

    calibrated = torch.softmax(
        logits / inference.TEMPERATURE,
        dim=1,
    )

    expected = torch.softmax(
        logits / 1.627714614648346,
        dim=1,
    )

    assert torch.allclose(calibrated, expected, atol=1e-7)
    assert torch.isclose(calibrated.sum(), torch.tensor(1.0), atol=1e-7)

def test_tier2_predict_returns_valid_detection():
    result = inference.tier2_predict(
        "import sqlite3\nconn = sqlite3.connect('app.db')\n"
    )

    assert result.source == "codebert"
    assert result.predicted_label in {
        "CWE-22",
        "CWE-78",
        "CWE-79",
        "CWE-89",
        "SAFE",
    }
    assert result.confidence is not None
    assert 0.0 <= result.confidence <= 1.0

def test_tier2_predict_safe_code():
    result = inference.tier2_predict(
        "def add(a, b):\n"
        "    return a + b\n"
    )

    assert result.source == "codebert"
    assert result.predicted_label in {
        "CWE-22",
        "CWE-78",
        "CWE-79",
        "CWE-89",
        "SAFE",
    }
    assert result.confidence is not None
    assert 0.0 <= result.confidence <= 1.0

def test_tier1_predict_detects_sql_injection():
    result = inference.tier1_predict(
        "import sqlite3\n"
        "conn = sqlite3.connect('app.db')\n"
        "user_input = input()\n"
        "conn.execute('SELECT * FROM users WHERE id=' + user_input)\n"
    )

    assert result.source == "bandit"
    assert result.predicted_label == "CWE-89"

def test_scan_code_returns_scan_response():
    request = inference.CodeSnippetRequest(
        code="def add(a, b):\n    return a + b\n",
        file_path="test.py",
        function_name="add",
        start_line=1,
    )

    result = inference.scan_code(request)

    assert result.final_label in {
        "CWE-22",
        "CWE-78",
        "CWE-79",
        "CWE-89",
        "SAFE",
    }
    assert isinstance(result.is_vulnerable, bool)
    assert len(result.detections) >= 1