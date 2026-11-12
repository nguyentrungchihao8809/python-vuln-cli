from pathlib import Path

def read_file(filename):
    base_dir = Path("/var/www/files")
    file_path = base_dir / filename
    return file_path.read_text()

#cwe22
