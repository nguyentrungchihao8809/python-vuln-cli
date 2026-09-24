import os
import argparse

from ast_function_slicer import slice_functions
from inference import scan_code
from schemas import CodeSnippetRequest
from sarif_exporter import save_sarif

EXCLUDE_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules", "env"}


def find_python_files(target_path: str):
    """Neu target_path la file -> tra ve chinh no. Neu la thu muc -> quet dequy tim .py.""" 
    if os.path.isfile(target_path):
        if target_path.endswith(".py"):
            return [target_path]
        else:
            print(f"[CANH BAO] File khong phai .py, bo qua: {target_path}") //test
            return []

    py_files = []
    for root, dirs, files in os.walk(target_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return py_files


def scan_file(file_path: str):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        source_code = f.read()

    functions = slice_functions(source_code, include_nested=False)

    if isinstance(functions, dict) and "error" in functions:
        print(f"[LOI] {file_path}: Khong the phan tich (SyntaxError): {functions['error']}")
        return []

    if not functions:
        return []

    print(f"\n{'='*70}")
    print(f"QUET FILE: {file_path}")
    print(f"So ham tim thay: {len(functions)}")
    print('='*70)

    responses = []
    vulnerable_count = 0

    for func in functions:
        request = CodeSnippetRequest(
            code=func["code"],
            file_path=file_path,
            function_name=func["name"],
            start_line=func["start_line"]
        )
        response = scan_code(request)
        responses.append(response)

        status_icon = "[CANH BAO]" if response.is_vulnerable else "[OK]      "
        print(f"\n{status_icon} Ham: {func['name']} (dong {func['start_line']}-{func['end_line']})")
        print(f"           Ket qua: {response.final_label}")

        if response.is_vulnerable:
            vulnerable_count += 1
            for det in response.detections:
                conf_str = f"{det.confidence:.2f}" if det.confidence is not None else "N/A"
                print(f"           - {det.source}: {det.predicted_label} (confidence={conf_str})")

    print(f"\n{'-'*70}")
    print(f"Ket qua file: {vulnerable_count}/{len(functions)} ham co canh bao")

    return responses


def scan_target(target_path: str):
    py_files = find_python_files(target_path)

    if not py_files:
        print(f"[THONG BAO] Khong tim thay file .py nao de quet trong: {target_path}")
        return []

    print(f"Tim thay {len(py_files)} file .py can quet.")

    all_responses = []
    for file_path in py_files:
        responses = scan_file(file_path)
        all_responses.extend(responses)

    total_functions = len(all_responses)
    total_vulnerable = sum(1 for r in all_responses if r.is_vulnerable)

    print(f"\n{'='*70}")
    print(f"TONG KET TOAN BO: {total_vulnerable}/{total_functions} ham co canh bao")
    print(f"Tren {len(py_files)} file da quet")
    print('='*70)

    return all_responses


def main():
    parser = argparse.ArgumentParser(description="CLI quet lo hong bao mat trong ma nguon Python do AI sinh ra")
    parser.add_argument("path", help="Duong dan den file hoac thu muc Python can quet")
    parser.add_argument("--sarif", help="Duong dan file SARIF output (tuy chon)", default=None)
    args = parser.parse_args()

    responses = scan_target(args.path)

    if args.sarif and responses:
        path = save_sarif(responses, args.sarif)
        print(f"\nDa xuat ket qua SARIF tai: {path}")


if __name__ == "__main__":
    main()
