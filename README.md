# AI Code Vulnerability Detector

> **Hệ thống phát hiện lỗ hổng bảo mật trong mã nguồn Python do AI sinh ra kết hợp Phân tích tĩnh (SAST) và Học máy / Học sâu (CodeBERT).**

---

## Tổng quan dự án (Project Overview)

Trong bối cảnh lập trình viên ngày càng ứng dụng các công cụ AI hỗ trợ sinh mã nguồn (như ChatGPT, GitHub Copilot), nguy cơ mã nguồn được tạo ra chứa các điểm yếu bảo mật chưa được kiểm duyệt là rất lớn. Dự án **AI Code Vulnerability Detector** được phát triển nhằm tự động hóa quy trình rà soát, phát hiện và phân loại các điểm yếu bảo mật trong mã nguồn Python trước khi hợp nhất vào các dự án phần mềm.

Hệ thống tận dụng ưu điểm của phương pháp phân tích tĩnh (Static Analysis - SAST) để quét nhanh theo luật, kết hợp với mô hình học sâu **CodeBERT** fine-tuned nhằm phân tích ngữ nghĩa sâu của mã nguồn đối với các trường hợp phức tạp.

---

## Kiến trúc hệ thống (System Architecture)

Luồng xử lý (Inference Pipeline):

Source Code (.py) 
    └── AST Function Slicer (python ast module)
            └── Tier 1: Static Analysis (Bandit / Semgrep)
                    ├── Vulnerable (Fast-pass) ──> Security Report
                    └── SAFE ──> Tier 2: ML / CodeBERT Fallback
                                    └── Calibrated Logits (Temperature Scaling) ──> SARIF / CLI Output

### Các thành phần chính:
- **AST Function Slicer**: Phân tích cây cú pháp trừu tượng (Abstract Syntax Tree) bằng thư viện  gốc của Python để trích xuất mã nguồn ở mức hàm (function-level slicing).
- **Tier 1 (SAST - Static Analysis)**: Tích hợp công cụ **Bandit (v1.9.4)** và quy tắc custom **Semgrep** nhằm phát hiện nhanh các lỗi bảo mật phổ biến.
- **Tier 2 (Machine Learning / Deep Learning)**: Mô hình **CodeBERT fine-tuned (5 classes)** xử lý các hàm được Tier 1 đánh giá là SAFE nhằm giảm tỷ lệ bỏ sót lỗi (False Negative).
- **Temperature Calibration**: Chuẩn hóa xác suất dự đoán của CodeBERT bằng thuật toán Temperature Scaling ( pprox 1.6277$), giúp tăng độ tin cậy của chỉ số confidence score.
- **SARIF & CI/CD Integration**: Định dạng kết quả đầu ra theo chuẩn công nghiệp SARIF v2.1.0, hỗ trợ tích hợp trực tiếp vào quy trình tự động hóa GitHub Actions.

---

## Phạm vi phát hiện lỗ hổng (Supported CWEs)

Hệ thống tập trung phát hiện 5 nhóm danh mục lỗ hổng bảo mật chuẩn (CWE) phổ biến trên ngôn ngữ Python và nhãn mã nguồn an toàn (SAFE):

| Stt | Class / CWE ID | Tên danh mục CWE (CWE Category) | Ghi chú / Mô tả |
| :-: | :--- | :--- | :--- |
| 1 | **CWE-22** | Path Traversal | Duyệt đường dẫn thư mục trái phép |
| 2 | **CWE-78** | OS Command Execution | Chèn lệnh hệ điều hành |
| 3 | **CWE-79** | XSS Vulnerability | Chèn kịch bản kịch bản giao diện |
| 4 | **CWE-89** | SQL Query Security | Chèn câu lệnh SQL trái phép vào cơ sở dữ liệu |
| 5 | **CWE-798** | Hardcoded Secrets | Lộ mật khẩu, token hoặc API key cứng trong mã nguồn |
| 0 | **SAFE** | Non-vulnerable Code | Đoạn mã nguồn an toàn |

---

## Bộ dữ liệu & Kết quả đánh giá (Datasets & Benchmark)

### 1. Tập dữ liệu (Datasets)
- **In-Distribution (Huấn luyện & Kiểm thử)**: Trích xuất từ cơ sở dữ liệu **CVEfixes** (đã lọc riêng các dự án Python) và **Bandit Test Corpus**.
- **Out-of-Distribution (OOD Test Set)**: Sử dụng các bộ benchmark tiêu chuẩn **SecurityEval** và **CyberSecEval** nhằm đánh giá khả năng tổng quát hóa trên mã nguồn do AI sinh ra.

### 2. Kết quả đánh giá tiêu chuẩn (84 Test Samples)
Thử nghiệm được thực hiện trên 84 mẫu test tiêu chuẩn (49 SAFE, 35 Vulnerable):

| Mô hình / Pipeline | Accuracy | Macro-F1 | Weighted-F1 | Vulnerability FNR | Security FPR |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Bandit-only** | 57.14% | 26.50% | 45.06% | 88.57% | 10.20% |
| **CodeBERT-only** | 46.43% | 48.17% | 47.39% | 57.14% | 51.02% |
| **Cascading Ensemble** | 42.86% | 44.16% | 43.12% | 54.29% | 59.18% |

### 3. Tối ưu hóa & Xuất bản (Optimization)
- **Temperature Scaling Calibration**:  = 1.627714$, giúp cải thiện chỉ số ECE từ -bash.3301 
ightarrow 0.1779$ trên tập test.
- **ONNX Runtime Export**: Xuất mô hình CodeBERT sang định dạng ONNX, đạt độ chính xác tương đương PyTorch với sai lệch tối đa absolute diff $pprox 3.07 	imes 10^-6$.

---

## Cấu trúc dự án (Directory Structure)

dataset_py/
├── app/
│   ├── cli.py                  # Giao diện dòng lệnh quét mã nguồn
│   └── inference.py            # Pipeline xử lý suy luận (Bandit-first + CodeBERT)
├── dataset/
│   ├── train_dataset_v1.csv    # Dữ liệu huấn luyện
│   ├── val_split.csv           # Dữ liệu validation
│   └── test_split.csv          # Dữ liệu test chính thức (84 samples)
├── models/
│   ├── codebert_finetuned/     # Model CodeBERT fine-tuned 5 classes
│   └── codebert_5class_calibration/ # Cấu hình Temperature Scaling
├── script/
│   ├── 05_extract_dataset.py   # Trích xuất dữ liệu từ SQLite CVEfixes
│   ├── 26_split_train_test.py  # Phân chia dữ liệu train/val/test
│   └── 27_evaluate_models.py   # Script đánh giá mô hình chuẩn hóa
├── test/
│   ├── demo_tier2.py           # File mã nguồn mẫu kiểm thử
│   └── demo_tier2.sarif        # File báo cáo kết quả định dạng SARIF
├── CVEfixes.db                 # Cơ sở dữ liệu SQLite chứa các commit/vulnerability
└── README.md                   # Tài liệu hướng dẫn sử dụng dự án

---

## Hướng dẫn cài đặt & Sử dụng (Getting Started)

### 1. Yêu cầu hệ thống
- **OS**: Windows 11 / Linux / macOS
- **Python**: Version 3.10 trở lên (Đã thử nghiệm trên Python 3.13.7)
- **Bandit**: 

### 2. Cài đặt môi trường
# Clone repository
git clone <repository-url>
cd ai-code-vulnerability-detector

# Cài đặt các thư viện cần thiết
pip install -r requirements.txt

### 3. Chạy đơn vị kiểm thử (Pytest)
python -m pytest .\test -v

### 4. Quét mã nguồn bằng CLI
# Quét file mã nguồn Python và hiển thị kết quả
python app\cli.py test\demo_tier2.py

# Quét và xuất báo cáo theo chuẩn SARIF
python app\cli.py test\demo_tier2.py --sarif test\demo_tier2.sarif

## License
Dự án được bảo hộ và chia sẻ dưới giấy phép **MIT License**.
