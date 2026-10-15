
from pathlib import Path


BASE_DIR = Path("uploads")


def read_file(filename):
    file_path = BASE_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def download_file(filename):
    file_path = BASE_DIR / filename

    with open(file_path, "rb") as file:
        content = file.read()

    return content


def delete_file(filename):
    file_path = BASE_DIR / filename

    if file_path.exists():
        file_path.unlink()
        return True

    return False
