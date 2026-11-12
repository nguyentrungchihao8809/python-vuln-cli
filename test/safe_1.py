from pathlib import Path

def download_report(report_name):
    base = Path("/srv/reports").resolve()
    target = (base / report_name).resolve()
    if base not in target.parents:
        raise ValueError("Duong dan khong hop le")
    return target.read_bytes()