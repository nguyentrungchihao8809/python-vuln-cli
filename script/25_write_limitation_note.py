NOTE = """
GHI CHÚ HẠN CHẾ DỮ LIỆU - CWE-798 (Hardcoded Secrets)
======================================================

1. Nguồn CVEfixes: 0 mẫu ở mức method-level.
   Lý do: Hardcoded secrets thường nằm ở module-level (biến global, file config),
   không nằm trong thân hàm, nên bị bỏ sót khi trích xuất theo method_change.

2. Nguồn Bandit Test Corpus: chỉ 9 mẫu (8 vulnerable / 1 safe).
   Lý do: Bandit Test Corpus là tập ví dụ minh họa (mỗi pattern lỗi chỉ có
   1-2 file), không phải tập dữ liệu lớn dùng để huấn luyện.

3. Quyết định xử lý:
   - Không loại CWE-798 khỏi phạm vi đề tài (giữ đúng cam kết trong đề cương).
   - Không dùng CWE-798 trong so sánh định lượng chính (Precision/Recall/F1
     tổng hợp theo CWE) vì số mẫu quá nhỏ, không đủ ý nghĩa thống kê.
   - Đưa CWE-798 vào phần đánh giá định tính / phân tích riêng biệt trong
     chương Kết quả nghiên cứu, ghi rõ đây là hạn chế của nguồn dữ liệu công khai.
   - Cân nhắc bổ sung qua SecurityEval/CyberSecEval (OOD set) nếu có mẫu phù hợp,
     nhưng không dùng để huấn luyện (chỉ dùng đánh giá).
"""

with open("../dataset/LIMITATION_NOTE_CWE798.md", "w", encoding="utf-8") as f:
    f.write(NOTE)

print("Đã lưu ghi chú hạn chế tại: ../dataset/LIMITATION_NOTE_CWE798.md")