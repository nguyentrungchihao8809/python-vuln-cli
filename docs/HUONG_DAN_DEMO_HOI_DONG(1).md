# Hướng dẫn Demo Dự án trước Hội đồng

**Đề tài:** Hệ thống phát hiện lỗ hổng bảo mật trong mã nguồn Python do AI sinh ra kết hợp Phân tích tĩnh và Học máy

**Sinh viên:** Nguyễn Trung Chí Hào (Data & ML) — Nguyễn Thị Thanh Vân (Software & Integration)

---

## 1. Chuẩn bị trước buổi demo

### 1.1. Checklist cần kiểm tra trước 1 ngày

- [ ] Máy tính có kết nối Internet ổn định nếu cần tải model từ Hugging Face; khi demo nên ưu tiên model local tại `models/codebert_finetuned/`
- [ ] Đã cài đặt đầy đủ thư viện: `pip install -r requirements.txt`
- [ ] Đã test chạy thử toàn bộ kịch bản demo ít nhất 1 lần, đúng thứ tự
- [ ] Repo GitHub đã push code mới nhất
- [ ] Mở sẵn các tab trình duyệt cần thiết
- [ ] Chuẩn bị sẵn 2-3 file code mẫu để demo trực tiếp, phòng trường hợp hội đồng yêu cầu mẫu code khác
- [ ] Kiểm tra model local là **CodeBERT 5-class**, không phải checkpoint 6-class cũ
- [ ] Kiểm tra file calibration: `models/codebert_5class_calibration/temperature_scaling.json`
- [ ] Nếu trình diễn ONNX, kiểm tra `models/codebert_onnx/model.onnx` đã có sẵn

### 1.2. Các tab trình duyệt cần mở sẵn

1. Repo GitHub: `https://github.com/nguyentrungchihao8809/python-vuln-cli`
2. Tab Actions: `https://github.com/nguyentrungchihao8809/python-vuln-cli/actions`
3. Tab Security → Code scanning: `https://github.com/nguyentrungchihao8809/python-vuln-cli/security/code-scanning`
4. Model trên Hugging Face: `https://huggingface.co/haoday333/python-vuln-codebert`
5. File kết quả số liệu trong thư mục `models/`, nếu cần trình bày

### 1.3. Cửa sổ terminal cần chuẩn bị

Mở PowerShell tại thư mục gốc dự án:

```powershell
cd D:\Projects\dataset_py
```

Đảm bảo đang dùng đúng môi trường Python có đầy đủ thư viện.

---

## 2. Kịch bản Demo

Thời lượng đề xuất: **12-15 phút**.

### Phần A — Giới thiệu bài toán và dữ liệu (2 phút, dùng slide)

Trình bày ngắn gọn:

- Vấn đề: mã nguồn do AI sinh ra có thể chứa lỗ hổng bảo mật.
- Mục tiêu: phát hiện các nhóm lỗ hổng Python được chọn trong phạm vi nghiên cứu.
- Kiến trúc tổng thể: Source Code → AST Function Slicer → Static Analysis + ML → Security Report / CLI.
- Hệ thống thực tế sử dụng **Bandit ở Tier 1** và **CodeBERT ở Tier 2**.
- CodeBERT được huấn luyện theo bài toán **5-class hiện tại**:
  - `CWE-22`
  - `CWE-78`
  - `CWE-79`
  - `CWE-89`
  - `SAFE`

**Lưu ý:** CWE-798 (Hardcoded Secrets) vẫn được hỗ trợ ở lớp static analysis/Bandit mapping, nhưng **không còn là class của mô hình ML hiện tại** do dữ liệu CVEfixes ở mức method-level không đủ để đưa vào huấn luyện định lượng.

---

### Phần B — Demo dữ liệu và mô hình (3 phút)

#### Bước 1: Cho hội đồng xem phạm vi dữ liệu

Dataset hiện tại sử dụng:

- **CVEfixes**: nguồn chính cho các mẫu vulnerable/safe từ lịch sử sửa lỗi.
- **Bandit Test Corpus**: nguồn bổ sung cho static-analysis/security samples.
- **SecurityEval và CyberSecEval**: dùng cho đánh giá OOD, không đưa vào tập train hiện tại.

Tập dữ liệu đã được chia thành:

- Train: **392 samples**
- Validation: **84 samples**
- Test: **84 samples**

Tổng sau khi loại CWE-798 khỏi bài toán ML: **560 samples**.

Tỷ lệ chia: **70% / 15% / 15%**.

Có kiểm tra leakage giữa các split theo:

- `sample_id`
- `origin_ref`
- exact code

và không có overlap giữa Train/Validation/Test theo các kiểm tra này.

#### Bước 2: Giải thích vấn đề CWE-798

Có thể cho hội đồng xem:

```powershell
type dataset\LIMITATION_NOTE_CWE798.md
```

Cách trình bày:

> CWE-798 được giữ lại trong phạm vi static analysis và tài liệu provenance, nhưng không đưa vào 5-class ML training vì dữ liệu method-level không đủ. Nhóm không cố tạo dữ liệu tổng hợp để bù số lượng, nhằm giữ tính trung thực của thực nghiệm.

#### Bước 3: Cho xem checkpoint/model configuration

Model hiện tại:

```text
models\codebert_finetuned\
```

Model có:

```text
num_labels = 5

0 → CWE-22
1 → CWE-78
2 → CWE-79
3 → CWE-89
4 → SAFE
```

Checkpoint 6-class cũ đã được tách khỏi model chính và không dùng cho kết quả hiện tại.

#### Bước 4: Giải thích calibration

Model hiện tại có thêm **temperature scaling** để hiệu chỉnh confidence.

File:

```text
models\codebert_5class_calibration\temperature_scaling.json
```

Temperature được fit **chỉ trên Validation**, sau đó áp dụng cho Test.

Giá trị hiện tại:

```text
T = 1.627714614648346
```

Calibration không thay đổi class prediction, nhưng làm confidence hợp lý hơn.

Kết quả trên Validation:

```text
Accuracy        = 60.71%
NLL             giảm từ 1.096880 xuống 0.973032
ECE             giảm từ 0.246727 xuống 0.131162
Mean confidence giảm từ 0.809131 xuống 0.662166
```

Trên Test:

```text
Accuracy        = 46.43%
NLL             giảm từ 1.299870 xuống 1.114268
ECE             giảm từ 0.330057 xuống 0.177886
Prediction      không thay đổi sau calibration
```

**Không nên trình bày accuracy Test 46.43% như một kết quả tốt.** Đây là kết quả thực nghiệm hiện tại và cần được phân tích tiếp bằng confusion matrix và per-class metrics trước khi đưa ra kết luận về chất lượng mô hình.

---

## 3. Demo CLI quét trực tiếp (5 phút)

Đây là phần quan trọng nhất của buổi demo.

### Bước 1: Cho hội đồng xem file mẫu

```powershell
type test\sample_vuln.py
```

### Bước 2: Chạy CLI

```powershell
python app\cli.py test\sample_vuln.py --sarif test\demo_output.sarif.json
```

### Bước 3: Giải thích pipeline

Luồng xử lý thực tế:

```text
Python source
    ↓
AST function slicing
    ↓
Tier 1: Bandit
    ↓
Nếu Bandit phát hiện → ghi nhận static finding
    ↓
Nếu cần ML → Tier 2: CodeBERT 5-class
    ↓
Temperature scaling cho confidence
    ↓
ScanResponse
    ↓
CLI / SARIF
```

Không nên nói rằng Tier 1 luôn "đúng tuyệt đối". Bandit là rule-based static analysis và có thể có false positive/false negative tùy rule và ngữ cảnh.

### Bước 4: Giải thích kết quả

Chỉ rõ:

- file/function được quét
- CWE được phát hiện
- nguồn phát hiện: `bandit` hoặc `codebert`
- confidence nếu kết quả đến từ CodeBERT
- final label và trạng thái vulnerable/safe

### Bước 5: Demo code trực tiếp

Nếu hội đồng đưa code tại chỗ:

1. Dán code vào một file `.py`.
2. Chạy lại CLI.
3. Giải thích kết quả theo đúng `ScanResponse`.

Nếu cần kịch bản dự phòng:

```powershell
@'
from flask import request
from markupsafe import Markup

def render_comment(user_comment):
    return Markup(user_comment)
'@ | Set-Content -Path test\demo_xss.py -Encoding utf8

python app\cli.py test\demo_xss.py
```

### Bước 6: Demo quét cả thư mục

```powershell
python app\cli.py test --sarif test\demo_all.sarif.json
```

---

## 4. Demo CI/CD tích hợp GitHub Action (3 phút)

### Bước 1

Mở tab GitHub Actions và chỉ vào một hoặc vài lần chạy thành công.

### Bước 2

Giải thích workflow:

> Khi có push hoặc pull request, GitHub Action tự động chạy CLI để quét source code, tạo kết quả SARIF và đưa kết quả vào GitHub Code Scanning.

### Bước 3

Mở:

**GitHub → Security → Code scanning**

Cho hội đồng xem các alert đã được ghi nhận.

### Bước 4 — Nếu có thời gian

Có thể sửa một thay đổi nhỏ trên branch demo để minh họa workflow tự động được kích hoạt.

---

## 5. Demo đánh giá khoa học (phần bắt buộc)

Đây là phần cần trình bày **trung thực**, đặc biệt vì Test accuracy hiện tại thấp hơn majority baseline.

### 5.1. Kết quả hiện tại

Kết quả 5-class hiện tại:

| Metric | Validation | Test |
|---|---:|---:|
| Accuracy | 60.71% | 46.43% |
| Macro F1 | 60.10% | 48.17% |
| Weighted F1 | 60.95% | 47.39% |
| Majority baseline | 58.33% | 58.33% |

Majority baseline trên Test:

```text
SAFE = 49 / 84 = 58.33%
```

Vì vậy, **accuracy 46.43% hiện thấp hơn baseline 58.33%**.

Đây là vấn đề cần phân tích, không được che giấu trong báo cáo/demo.

### 5.2. Bước phân tích bắt buộc trước khi kết luận

Cần lấy prediction thực tế của toàn bộ:

```text
Validation = 84 samples
Test       = 84 samples
```

Sau đó tính:

1. Confusion matrix 5×5.
2. Precision từng class.
3. Recall từng class.
4. F1 từng class.
5. Macro F1.
6. Weighted F1.
7. Support từng class.
8. Majority baseline.
9. `VULNERABLE → SAFE` false negative.
10. `SAFE → VULNERABLE` false positive.
11. Danh sách toàn bộ test samples bị dự đoán sai.

Mục tiêu là xác định model đang sai theo kiểu nào:

```text
CWE → SAFE
```

→ bỏ sót vulnerability.

```text
SAFE → CWE
```

→ false positive.

```text
CWE-A → CWE-B
```

→ phát hiện được vulnerability nhưng phân loại sai CWE.

**Chưa được kết luận nguyên nhân là overfitting, data bug hay preprocessing bug trước khi có các kết quả này.**

### 5.3. Audit các sample dự đoán sai

Sau khi có confusion matrix, lấy toàn bộ test samples:

```text
y_true != y_pred
```

và audit code bằng tay.

Mỗi sample nên ghi lại:

| sample_id | true_label | predicted_label | confidence | source | origin_ref | nhận xét |
|---|---|---|---:|---|---|---|
| ... | ... | ... | ... | ... | ... | ... |

Mục tiêu của bước audit:

- xác định sample khó hay model sai thật
- phát hiện label bất thường
- kiểm tra before/after patch
- kiểm tra context bị mất do function-level slicing
- kiểm tra sự khác biệt giữa CVEfixes và Bandit
- xem Test có khó hơn Validation hay không

### 5.4. OOD evaluation

SecurityEval/CyberSecEval chỉ dùng cho **OOD evaluation**, không dùng để huấn luyện.

Không nên đưa một con số OOD cũ vào demo nếu chưa được tái xác nhận bằng pipeline 5-class hiện tại.

Cách trình bày an toàn:

> OOD được sử dụng để đánh giá khả năng tổng quát hóa. Kết quả OOD chính thức sẽ được báo cáo sau khi hoàn tất evaluation nhất quán với checkpoint 5-class hiện tại.

---

## 6. ONNX — phần mở rộng triển khai

ONNX được xem là **deployment extension**, không phải một mô hình ML khác.

File:

```text
models\codebert_onnx\model.onnx
```

Đã kiểm tra:

```text
ONNX Runtime load: OK
Output shape: [batch, 5]
PyTorch class = ONNX class
Prediction match = True
```

Sai khác logit giữa PyTorch và ONNX ở mức rất nhỏ:

```text
MAX_ABS_DIFF  ≈ 3.07e-06
MEAN_ABS_DIFF ≈ 1.12e-06
```

Có thể trình bày:

> ONNX được sử dụng để kiểm tra khả năng triển khai inference ở định dạng trung gian, trong khi PyTorch/Transformers vẫn là implementation chính của mô hình.

Không cần trình diễn ONNX nếu thời gian demo bị giới hạn.

---

## 7. Câu hỏi dự kiến từ Hội đồng

### Q1: Tại sao Test accuracy chỉ 46.43%, thấp hơn majority baseline 58.33%?

**Trả lời:**

> Đây là hạn chế hiện tại của mô hình và nhóm không che giấu kết quả này. Majority baseline trên Test là 58.33%, trong khi CodeBERT đạt 46.43%. Trước khi kết luận nguyên nhân, nhóm phân tích confusion matrix và per-class precision/recall/F1 để xác định model chủ yếu sai theo hướng bỏ sót vulnerability, báo động nhầm hay nhầm giữa các CWE. Sau đó mới audit các test samples bị dự đoán sai.

### Q2: Tại sao Validation 60.71% nhưng Test chỉ 46.43%?

**Trả lời:**

> Có khoảng cách khoảng 14.29 điểm phần trăm. Đây là tín hiệu cần kiểm tra về khả năng tổng quát hóa. Nhóm không kết luận ngay là overfitting mà kiểm tra confusion matrix, per-class metrics và từng sample sai để phân biệt giữa class imbalance, độ khó của Test, distribution shift và vấn đề dữ liệu.

### Q3: Tại sao không dùng luôn majority baseline?

**Trả lời:**

> Majority baseline chỉ luôn dự đoán SAFE. Nó là mốc tham chiếu để biết mô hình có thực sự học được tín hiệu phân loại hay không. Với bài toán security, chỉ dự đoán SAFE có thể cho accuracy khá do mất cân bằng lớp nhưng lại bỏ sót vulnerability. Vì vậy cần xem Recall và F1 từng CWE, đặc biệt là false negative.

### Q4: CWE-798 tại sao không còn là class của ML?

**Trả lời:**

> Dữ liệu method-level cho CWE-798 không đủ để huấn luyện một class đáng tin cậy. Nhóm không tạo dữ liệu tổng hợp để bù số lượng. Vì vậy CWE-798 được loại khỏi 5-class ML training, nhưng khả năng phát hiện hardcoded secrets của Bandit vẫn được giữ trong static-analysis layer.

### Q5: Tại sao mô hình chính là CodeBERT thay vì Cascading Ensemble?

**Trả lời:**

> Đề cương ban đầu định hướng Cascading Ensemble. Tuy nhiên trong thực nghiệm, các cấu hình cascading đã thử không vượt CodeBERT đơn lẻ về F1-macro. Vì vậy nhóm chọn CodeBERT làm ML model chính theo kết quả thực nghiệm, còn Bandit vẫn được tích hợp ở static-analysis layer. Đây là quyết định dựa trên kết quả thực nghiệm thay vì cố giữ kiến trúc ban đầu bằng mọi giá.

### Q6: Temperature scaling có làm accuracy tốt hơn không?

**Trả lời:**

> Không. Temperature scaling không thay đổi class prediction trong kết quả hiện tại. Mục đích của nó là calibration confidence. Trên Validation, ECE giảm từ 0.246727 xuống 0.131162 và NLL giảm từ 1.096880 xuống 0.973032. Trên Test, ECE giảm từ 0.330057 xuống 0.177886 và NLL giảm từ 1.299870 xuống 1.114268.

### Q7: Vì sao không tạo thêm dữ liệu bằng LLM?

**Trả lời:**

> Nhóm chủ động không sử dụng dữ liệu synthetic/LLM-generated làm training data chính. Với đề tài nghiên cứu sinh viên, provenance và tính kiểm chứng của dữ liệu quan trọng hơn việc tăng số lượng mẫu bằng dữ liệu tổng hợp.

### Q8: Function-level slicing có hạn chế gì?

**Trả lời:**

> Function-level slicing giúp chuẩn hóa sample và giảm kích thước input, nhưng có thể làm mất context liên hàm. Một vulnerability có thể phụ thuộc vào dữ liệu hoặc behavior ở function khác. Đây là một limitation của thiết kế hiện tại và là hướng cải tiến trong tương lai.

### Q9: Vì sao inference có thể mất thời gian?

**Trả lời:**

> CodeBERT sử dụng giới hạn input tối đa 512 tokens. Với input ngắn, một phần tài nguyên vẫn được sử dụng cho sequence đã padding. Dynamic padding và batch inference là các hướng tối ưu tiếp theo.

### Q10: Nhóm chia công việc giữa 2 thành viên như thế nào?

**Trả lời:**

> SV A phụ trách dữ liệu, preprocessing, huấn luyện và đánh giá ML. SV B phụ trách API/CLI, integration và CI/CD. Điểm tích hợp giữa hai phần là contract Pydantic, đặc biệt `CodeSnippetRequest` và `ScanResponse`.

---

## 8. Xử lý sự cố trong lúc demo

| Sự cố | Cách xử lý |
|---|---|
| Không có Internet | Ưu tiên model local tại `models/codebert_finetuned/` nếu model đã có sẵn |
| CLI chạy chậm lúc load model | Giải thích đây là thời gian nạp model ban đầu; không đồng nghĩa thời gian inference cho từng file |
| Lệnh báo lỗi đường dẫn | Kiểm tra đang đứng tại `D:\Projects\dataset_py` |
| Hội đồng hỏi sâu về code | Mở `app/inference.py`, `app/schemas.py`, `app/cli.py` |
| Hội đồng hỏi về calibration | Mở `models/codebert_5class_calibration/temperature_scaling.json` |
| Hội đồng hỏi về ONNX | Mở `models/codebert_onnx/` và trình bày kết quả so sánh PyTorch/ONNX |
| GitHub Action đang chạy | Chuẩn bị sẵn một run thành công trước đó hoặc screenshot |
| Hội đồng hỏi tại sao Test thấp hơn baseline | Không né tránh; trình bày confusion matrix/per-class metrics và danh sách misclassified samples |

---

## 9. Lưu ý về thời gian

- Tổng thời gian demo nên gói gọn trong **12-15 phút**.
- Phần CLI là phần quan trọng nhất về mặt sản phẩm.
- Phần đánh giá khoa học là phần quan trọng nhất để chứng minh tính trung thực của thực nghiệm.
- Nếu thời gian rất hạn chế, có thể bỏ phần ONNX và rút ngắn GitHub Action.
- **Không nên dùng thời gian demo để che giấu kết quả Test thấp.** Nên chủ động trình bày đây là hạn chế hiện tại và cho thấy nhóm có quy trình phân tích lỗi rõ ràng.
- Các con số confusion matrix và per-class metrics phải được cập nhật từ prediction thực tế trước khi chốt báo cáo cuối cùng.
