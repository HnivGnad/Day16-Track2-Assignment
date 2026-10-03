Benchmark được thực hiện trên EC2 m7i-flex.large (CPU, 2 luồng), LightGBM 4.7.0 và toàn bộ 284.807 giao dịch Kaggle.
Dữ liệu được chia stratified thành 64% train, 16% validation và 20% test với seed 42; test không dùng cho early stopping.
Thời gian đọc CSV là 1.0045 giây; training mất 8.4721 giây với best iteration 332.
AUC-ROC trên test đạt 0.974047; average precision đạt 0.872112.
Tại ngưỡng 0,5, Precision=0.950617, Recall=0.785714, F1=0.860335.
Accuracy=0.999561; cần đối chiếu baseline luôn đoán không gian lận (0.998280) vì dữ liệu mất cân bằng.
Latency trung bình cho một dòng là 0.6198 ms, p95=0.6611 ms sau warmup.
Throughput batch 1.000 dòng đạt 85809.12 dòng/giây; phép đo chạy trong tiến trình Python, không bao gồm mạng/API.
Các thời gian phản ánh lần chạy này; tải hệ thống và loại instance có thể làm kết quả các lần chạy khác thay đổi.
