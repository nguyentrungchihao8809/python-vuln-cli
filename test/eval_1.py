import os

def download_report(report_name):
    path = os.path.join("/srv/reports", report_name)
    with open(path, "rb") as f:
        return f.read()