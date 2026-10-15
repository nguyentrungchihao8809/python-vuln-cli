
from pathlib import Path

import sqlite3


BASE_DIR = Path("uploads")


# CWE-22: Path Traversal
def read_file(filename):
    file_path = BASE_DIR / filename

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# CWE-22: Path Traversal
def download_file(filename):
    file_path = BASE_DIR / filename

    with open(file_path, "rb") as file:
        return file.read()

# CWE-79: Cross-Site Scripting (XSS)
def render_search_result(query):
    return f"<div>Search result: {query}</div>"


# CWE-798: Hardcoded Credentials
def connect_database():
    username = "admin"
    password = "Admin123!Hardcoded"

    connection = sqlite3.connect("app.db")
    return username, password, connection


def main():
    print("python detect vulnerabilities")


if __name__ == "__main__":
    main()
