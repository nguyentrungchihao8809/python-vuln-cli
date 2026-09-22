import ast

def slice_functions(source_code: str, include_nested: bool = False):
    """
    Tách các hàm từ source code Python.

    Args:
        source_code: mã nguồn Python dạng chuỗi.
        include_nested: True nếu muốn lấy cả hàm lồng bên trong hàm khác.

    Returns:
        List[dict]: mỗi dict gồm name, start_line, end_line, code, is_method (thuộc class hay không)
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {"error": f"SyntaxError: {e}"}

    functions = []

    def visit(node, parent_is_function=False, class_name=None):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if parent_is_function and not include_nested:
                    # bỏ qua hàm lồng nếu không yêu cầu lấy nested
                    continue
                                # Nếu có decorator, lấy dòng bắt đầu từ decorator đầu tiên
                if child.decorator_list:
                    actual_start = child.decorator_list[0].lineno
                else:
                    actual_start = child.lineno

                lines = source_code.splitlines()
                code = "\n".join(lines[actual_start - 1 : child.end_lineno])

                functions.append({
                    "name": child.name,
                    "class_name": class_name,
                    "start_line": actual_start,
                    "end_line": getattr(child, "end_lineno", child.lineno),
                    "code": code
                })
                # tiếp tục duyệt bên trong để tìm nested nếu cần
                visit(child, parent_is_function=True, class_name=class_name)
            elif isinstance(child, ast.ClassDef):
                visit(child, parent_is_function=parent_is_function, class_name=child.name)
            else:
                visit(child, parent_is_function=parent_is_function, class_name=class_name)

    visit(tree)
    return functions


if __name__ == "__main__":
    # Test 1: code có decorator
    sample_code_decorator = '''
class Handler:
    @staticmethod
    def process(data):
        return data.strip()

    @app.route("/api")
    def api_endpoint():
        pass
'''
    print("=== TEST 1: DECORATOR ===")
    result = slice_functions(sample_code_decorator, include_nested=False)
    for f in result:
        print(f"Name: {f['name']} | Lines: {f['start_line']}-{f['end_line']}")
        print(f['code'])
        print("---")

    # Test 2: code lỗi cú pháp
    sample_code_broken = '''
def broken_func(a, b)
    return a + b
'''
    print("\n=== TEST 2: SYNTAX ERROR ===")
    result2 = slice_functions(sample_code_broken)
    print(result2)