import json
from typing import List
from schemas import ScanResponse

# Mapping CWE -> mo ta ngan gon (dung cho SARIF rule description)
CWE_DESCRIPTIONS = {
    "CWE-89": "SQL Injection",
    "CWE-798": "Use of Hard-coded Credentials",
    "CWE-22": "Path Traversal",
    "CWE-78": "OS Command Injection",
    "CWE-79": "Cross-Site Scripting (XSS)",
}

# Mapping CWE -> muc do nghiem trong (dung chuan SARIF: error/warning/note)
CWE_SEVERITY = {
    "CWE-89": "error",
    "CWE-798": "error",
    "CWE-22": "warning",
    "CWE-78": "error",
    "CWE-79": "warning",
}


def build_sarif_rules() -> list:
    """Xay dung danh sach 'rules' khai bao truoc, dung chung cho toan bo SARIF report."""
    rules = []
    for cwe_id, desc in CWE_DESCRIPTIONS.items():
        rules.append({
            "id": cwe_id,
            "name": desc.replace(" ", ""),
            "shortDescription": {"text": desc},
            "fullDescription": {"text": f"Phat hien boi he thong ket hop phan tich tinh va hoc may: {desc}"},
            "defaultConfiguration": {"level": CWE_SEVERITY.get(cwe_id, "warning")}
        })
    return rules


def build_sarif_report(responses: List[ScanResponse], tool_name: str = "python-vuln-cli", tool_version: str = "1.0.0") -> dict:
    """Chuyen danh sach ScanResponse thanh 1 SARIF report hoan chinh."""
    results = []

    for resp in responses:
        if not resp.is_vulnerable:
            continue  # SARIF chi liet ke cac finding, khong liet ke ket qua "sach"

        cwe_id = resp.final_label
        req = resp.request

        result_entry = {
            "ruleId": cwe_id,
            "level": CWE_SEVERITY.get(cwe_id, "warning"),
            "message": {
                "text": f"Phat hien {CWE_DESCRIPTIONS.get(cwe_id, cwe_id)} trong ham '{req.function_name or 'unknown'}'."
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": req.file_path or "unknown_file.py"},
                        "region": {"startLine": req.start_line or 1}
                    }
                }
            ],
            "properties": {
                "detections": [d.model_dump() for d in resp.detections]
            }
        }
        results.append(result_entry)

    sarif_report = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": tool_name,
                        "version": tool_version,
                        "informationUri": "https://github.com/your-org/python-vuln-cli",
                        "rules": build_sarif_rules()
                    }
                },
                "results": results
            }
        ]
    }
    return sarif_report


def save_sarif(responses: List[ScanResponse], output_path: str):
    report = build_sarif_report(responses)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return output_path


if __name__ == "__main__":
    # Test nhanh voi du lieu gia
    from schemas import CodeSnippetRequest, DetectionResult

    fake_response = ScanResponse(
        request=CodeSnippetRequest(code="os.system(cmd)", file_path="test.py", function_name="run_command", start_line=4),
        final_label="CWE-78",
        is_vulnerable=True,
        detections=[DetectionResult(source="bandit", predicted_label="CWE-78", confidence=None)]
    )

    path = save_sarif([fake_response], "test_output.sarif.json")
    print(f"Da luu SARIF test tai: {path}")

    with open(path, "r", encoding="utf-8") as f:
        print(f.read())