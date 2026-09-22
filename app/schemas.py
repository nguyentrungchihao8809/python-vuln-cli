from pydantic import BaseModel, Field
from typing import Optional, List


class CodeSnippetRequest(BaseModel):
    """Input chuẩn cho mọi hàm inference - đại diện cho 1 đoạn code cần quét."""
    code: str = Field(..., description="Nội dung mã nguồn Python cần quét")
    file_path: Optional[str] = Field(None, description="Đường dẫn file gốc (nếu có), dùng cho báo cáo SARIF")
    function_name: Optional[str] = Field(None, description="Tên hàm (nếu đã tách qua AST Function Slicer)")
    start_line: Optional[int] = Field(None, description="Dòng bắt đầu của đoạn code trong file gốc")


class DetectionResult(BaseModel):
    """Kết quả phát hiện từ 1 nguồn (Bandit hoặc CodeBERT)."""
    source: str = Field(..., description="Nguồn phát hiện: 'bandit' hoặc 'codebert'")
    predicted_label: str = Field(..., description="Nhãn dự đoán: SAFE hoặc 1 trong 5 CWE")
    confidence: Optional[float] = Field(None, description="Độ tin cậy (0-1), None nếu là rule-based không có xác suất")


class ScanResponse(BaseModel):
    """Output chuẩn cho mọi hàm inference - kết quả quét 1 đoạn code."""
    request: CodeSnippetRequest
    final_label: str = Field(..., description="Nhãn cuối cùng hệ thống kết luận")
    is_vulnerable: bool = Field(..., description="True nếu final_label != SAFE")
    detections: List[DetectionResult] = Field(default_factory=list, description="Chi tiết kết quả từ từng nguồn")


if __name__ == "__main__":
    # Test nhanh
    req = CodeSnippetRequest(code="os.system(user_input)", file_path="test.py", start_line=10)
    print(req.model_dump_json(indent=2))