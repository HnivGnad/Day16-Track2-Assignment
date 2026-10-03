# Tiến độ Lab 16 AWS

`benchmark.py` thực hiện bước 4.4 trên bộ dữ liệu đầy đủ, giữ riêng tập validation cho early stopping và xuất metrics cùng báo cáo 9 dòng từ kết quả thật.
`run_benchmark.sh` lưu output benchmark và ảnh chụp số liệu dạng văn bản sau khi chạy; các file văn bản này không thay thế screenshot bắt buộc.

Đã kết nối Compute Node qua Bastion, xác nhận thư viện cài thành công và tải đủ dataset từ URL công khai chính thức của Kaggle bằng `download_dataset.py`, không cần API key hay điền thông tin cá nhân.
Compute Node đã dùng cho benchmark là `m7i-flex.large`, không phải `t3.medium` mặc định trong README. Báo cáo ghi loại máy thực tế.
Người thực hiện đã xác nhận nhận được `Destroy complete!`; kiểm tra lại Terraform state local thấy không còn tài nguyên được quản lý hoặc outputs. Phần 7 đã hoàn tất. Các lệnh SSH bên dưới chỉ còn là tài liệu tham khảo cho lúc hạ tầng còn hoạt động.

## Checklist nộp bài

- [x] Bước 4.3: dataset đã được tải vào `~/ml-benchmark/creditcard.csv`, kiểm tra đủ 284.807 dòng, 492 giao dịch gian lận và 31 cột chuẩn.
- [x] Bước 4.4: benchmark đã chạy thành công trên EC2; metrics, báo cáo và log đã tải về thư mục này.
- [x] Phần 5.1: có log `resource_usage.txt` và ảnh CPU/RAM/Network đã kiểm tra.
- [x] Phần 6.2 / 6.5 / 6.6: có JSON kết quả, archive mã nguồn Terraform và báo cáo 9 dòng.
- [x] Phần 6.1, bảng metrics: [`01_benchmark.png`](../01_benchmark.png) chứa đầy đủ metrics, khớp với JSON/báo cáo lần chạy lúc 21:00 ngày 03/10/2026.
- [ ] Phần 6.1, lệnh chạy: ảnh benchmark hiện bị cắt phần lệnh `python3 benchmark.py` và đầu output; bổ sung ảnh đã lưu chứa phần này nếu có. Không cần triển khai lại chỉ để chụp ảnh.
- [x] Phần 5.1 / 6.3: [`02_cpu.png`](../02_cpu.png) hiển thị CPU/RAM; [`03_ram_network.png`](../03_ram_network.png) hiển thị RAM và Network.
- [ ] Phần 5.2 / 6.4: lưu và đính kèm ảnh Bills đã cung cấp trong cuộc trò chuyện. Ảnh thể hiện Free plan, Billing tháng 10/2026 Pending và tổng 0 USD; người thực hiện báo số credit hiển thị vẫn là 100 USD. Chưa xác định chi phí sử dụng thực tế đã cập nhật. Có thể bổ sung ảnh khi AWS có dữ liệu mới.
- [x] Phần 7: người thực hiện xác nhận `Destroy complete!`; kiểm tra state local còn 0 tài nguyên được quản lý.

Ghi chú Billing để đính kèm bài nộp:
> Tại thời điểm kiểm tra, tài khoản AWS Free plan hiển thị Billing tháng 10/2026 tổng 0 USD, trạng thái Pending, và credit hiển thị 100 USD. Chưa xác định được chi phí sử dụng đã cập nhật; không kết luận lab không phát sinh chi phí. Hạ tầng đã được dọn dẹp bằng Terraform, với thông báo Destroy complete!.

## Lệnh tham khảo trước khi destroy

```powershell
ssh -F .local-lab/ssh_config lab-compute
```

Trên Compute Node, dataset và các script đã có sẵn:

```bash
cd ~/ml-benchmark
bash run_benchmark.sh
```

Lệnh trực tiếp để chụp phần benchmark:

```bash
cd ~/ml-benchmark
python3 benchmark.py
top
free -h
ip -s link
```

Nếu chạy lại để chụp screenshot, thoát SSH (`exit`), rồi tải kết quả mới từ PowerShell:

```powershell
scp -F .local-lab/ssh_config lab-compute:ml-benchmark/benchmark_result.json lab-compute:ml-benchmark/benchmark_metrics.md lab-compute:ml-benchmark/report.md deliverables/
```

Khi đó dùng `benchmark_metrics.md` mới để cập nhật bảng trong `README_aws.md`; bảng hiện đã đồng bộ với JSON và ảnh lần chạy hoàn tất lúc 21:00 ngày 03/10/2026 (Asia/Bangkok).

## Bộ file nộp bài

- `benchmark_result.json`: metrics từ lần chạy thật trên EC2.
- `benchmark_metrics.md`: bảng metrics được tạo từ cùng lần chạy.
- `report.md`: báo cáo ngắn 9 dòng được tạo từ cùng lần chạy.
- `benchmark_output.txt`, `resource_usage.txt`: output thực tế của benchmark và số liệu tài nguyên ngay sau đó.
- `terraform_source.zip`: mã nguồn Terraform và lockfile; không đóng gói private key, state, provider cache hoặc thông tin xác thực.
- Screenshot do bạn tự chụp: `01_benchmark.png`, `02_cpu.png`, `03_ram_network.png` ở thư mục gốc repo. File screenshot Billing chưa có trong repo.

Đối chiếu đầy đủ từng deliverable tại [`submission_audit.md`](submission_audit.md).

Phụ lục GPU + LLM là tùy chọn, chưa thực hiện trong luồng CPU này.

Tài liệu API: [LightGBM LGBMClassifier](https://lightgbm.readthedocs.io/en/latest/pythonapi/lightgbm.LGBMClassifier.html).
