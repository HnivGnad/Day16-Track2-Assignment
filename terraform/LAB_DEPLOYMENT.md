# Cấu hình đã dùng cho benchmark CPU

Terraform state trước khi destroy và metadata của EC2 xác nhận Compute Node đã dùng là `m7i-flex.large` (CPU), thay vì `t3.medium` mặc định trong `variables.tf`.
Bastion là `t3.micro`; region là `us-east-1`; luồng GPU chưa được bật.

Khi cần tái lập cùng loại Compute Node, dùng biến public sau (không chứa thông tin cá nhân):

```bash
terraform apply -var="cpu_instance_type=m7i-flex.large"
```

Lưu ý: lệnh apply tạo/thay đổi tài nguyên. Hạ tầng đã được destroy và state local không còn tài nguyên được quản lý; lệnh trên chỉ là tài liệu tái lập cấu hình đã dùng, không phải bước cần chạy để nộp bài.
Benchmark dùng seed 42, 2 luồng CPU, full Kaggle `mlg-ulb/creditcardfraud`, train/validation/test stratified 64%/16%/20%.
Mã benchmark nằm ở `benchmark.py` trong thư mục gốc repo, kết quả và báo cáo nằm ở `deliverables/`.

Archive source chỉ gồm code Terraform, shell scripts, lockfile và ghi chú này; không chứa private key, Terraform state, provider cache hoặc credentials.
Chỉ chạy `terraform destroy` sau khi đã tải kết quả về local và chụp đủ screenshot terminal, tài nguyên, Billing. Đợi `Destroy complete!`.
