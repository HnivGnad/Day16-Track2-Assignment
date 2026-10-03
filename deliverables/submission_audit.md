# Đối chiếu yêu cầu Lab 16 AWS

Kiểm tra ngày 03/10/2026 (Asia/Bangkok), theo phần 4–7 của `README_aws.md`.

| Yêu cầu | Trạng thái | Bằng chứng |
|---|---|---|
| 4.1–4.2: SSH Compute Node, kiểm tra thư viện | Đã thực hiện | Phiên SSH thực tế qua Bastion; environment trong JSON ghi Python và phiên bản thư viện |
| 4.3: full Credit Card Fraud Detection dataset | Đã thực hiện | JSON ghi 284.807 dòng, 492 fraud, 30 features, SHA-256; tải qua URL công khai Kaggle |
| 4.4 / 6.2: training, metrics, inference và JSON | Đủ | `benchmark.py`, `benchmark_result.json`, `benchmark_metrics.md`, `benchmark_output.txt`; kiểm tra các metrics và confusion matrix nhất quán |
| 6.1: screenshot terminal benchmark | Có metrics; thiếu phần lệnh trong ảnh | [`01_benchmark.png`](../01_benchmark.png) chứa đủ bảng, khớp JSON; phần `python3 benchmark.py` và đầu output bị cắt |
| 5.1 / 6.3: CPU/RAM/Network screenshot | Đủ | [`02_cpu.png`](../02_cpu.png), [`03_ram_network.png`](../03_ram_network.png); thêm log `resource_usage.txt` |
| 5.2 / 6.4: Billing screenshot | Chưa có file trong repo | Ảnh đã gửi trong cuộc trò chuyện thể hiện Free plan, Pending, tổng 0 USD; cần người thực hiện lưu ảnh vào repo |
| 6.5: ZIP mã nguồn Terraform | Đủ | `terraform_source.zip` gồm code, lockfile và ghi chú cấu hình; không có keys/state/credentials |
| 6.6: báo cáo ngắn 5–10 dòng | Đủ | `report.md` có 9 dòng, khớp JSON lần chạy 21:00 ngày 03/10/2026 |
| 7: dọn dẹp | Đã hoàn tất | Người thực hiện xác nhận `Destroy complete!`; state local có 0 managed resources và 0 outputs |
| Phụ lục GPU/vLLM | Không áp dụng | Tùy chọn theo README; bài này sử dụng CPU |

## Khác biệt cấu hình

Máy thực tế là `m7i-flex.large`, khác `t3.medium` mặc định trong README. Báo cáo và JSON đã ghi đúng loại máy; không diễn giải số liệu này thành benchmark trên `t3.medium`. Nếu giảng viên yêu cầu chính xác loại instance mặc định, cần xác nhận việc dùng CPU instance thay thế được chấp nhận.

## Thông tin còn cần người thực hiện bổ sung

1. Lưu ảnh Billing đã chụp thành `04_billing.png` trong thư mục gốc repo hoặc cung cấp đường dẫn file hiện có. Giữ đúng số 0 USD quan sát được và đính kèm ghi chú Free plan/Pending trong `README.md`; không thay bằng chi phí ước tính.
2. Nếu đã lưu ảnh benchmark có phần lệnh `python3 benchmark.py` và đầu output, bổ sung ảnh đó để đáp ứng đầy đủ yêu cầu screenshot terminal. Ảnh hiện có đã thể hiện toàn bộ bảng metrics.

Chưa thể kết luận bộ nộp đáp ứng đầy đủ tiêu chí screenshot khi hai mục trên chưa được bổ sung. Không cần thêm thông tin cá nhân hoặc API key để hoàn thiện các file hiện có.
