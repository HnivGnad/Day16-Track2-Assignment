#!/usr/bin/env python3
"""Run the required CPU LightGBM benchmark on the full Kaggle fraud dataset."""

import argparse
import hashlib
import inspect
import json
import os
import platform
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import lightgbm as lgb
import numpy as np
import pandas as pd
import sklearn
from sklearn.metrics import (
    accuracy_score, average_precision_score, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=Path("creditcard.csv"))
    parser.add_argument("--output", type=Path, default=Path("benchmark_result.json"))
    parser.add_argument("--threads", type=int, default=min(2, os.cpu_count() or 1))
    args = parser.parse_args()
    if args.threads < 1:
        parser.error("--threads must be at least 1")
    if not args.dataset.is_file():
        parser.error(f"Dataset not found: {args.dataset}. Complete README_aws.md step 4.3 first.")
    return args


def timed_predictions(model, rows, repetitions, threads):
    # Prepare input outside the timer and warm up before measuring model calls.
    for _ in range(5):
        model.predict_proba(rows, num_threads=threads)
    elapsed = []
    for _ in range(repetitions):
        start = perf_counter()
        model.predict_proba(rows, num_threads=threads)
        elapsed.append(perf_counter() - start)
    return np.asarray(elapsed)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def instance_type():
    """Read only EC2 hardware type via IMDSv2; never read credentials."""
    base = "http://169.254.169.254/latest/"
    try:
        request = urllib.request.Request(
            base + "api/token", method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            token = response.read().decode()
        request = urllib.request.Request(
            base + "meta-data/instance-type", headers={"X-aws-ec2-metadata-token": token},
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            return response.read().decode()
    except OSError:
        return "unknown (metadata unavailable)"


def main():
    args = arguments()
    print("LightGBM CPU benchmark | Kaggle mlg-ulb/creditcardfraud", flush=True)
    start = perf_counter()
    frame = pd.read_csv(args.dataset)
    load_seconds = perf_counter() - start
    expected_columns = {"Time", "Amount", "Class", *(f"V{i}" for i in range(1, 29))}
    if set(frame.columns) != expected_columns or len(frame) != 284807:
        raise ValueError("Expected the full creditcard.csv: 284807 rows and 31 standard columns.")
    if frame.isna().any().any() or not all(pd.api.types.is_numeric_dtype(t) for t in frame.dtypes):
        raise ValueError("Dataset must contain numeric values without missing entries.")
    if set(frame["Class"].unique()) != {0, 1} or int(frame["Class"].sum()) != 492:
        raise ValueError("Expected binary labels with 492 fraud transactions.")

    features = frame.drop(columns="Class").astype(np.float32)
    target = frame["Class"].astype(np.int8)
    # Keep test data completely separate from early stopping and model selection.
    x_development, x_test, y_development, y_test = train_test_split(
        features, target, test_size=0.20, random_state=42, stratify=target,
    )
    x_train, x_valid, y_train, y_valid = train_test_split(
        x_development, y_development, test_size=0.20, random_state=42,
        stratify=y_development,
    )
    model = lgb.LGBMClassifier(
        objective="binary", metric="average_precision", n_estimators=1000,
        learning_rate=0.05, num_leaves=31, min_child_samples=20, reg_lambda=1.0,
        n_jobs=args.threads, random_state=42, deterministic=True,
        force_col_wise=True, verbosity=-1,
    )
    print(f"Rows: {len(frame):,} | train/validation/test: "
          f"{len(x_train):,}/{len(x_valid):,}/{len(x_test):,} | threads: {args.threads}", flush=True)
    start = perf_counter()
    validation_args = (
        {"eval_X": x_valid, "eval_y": y_valid}
        if "eval_X" in inspect.signature(model.fit).parameters
        else {"eval_set": [(x_valid, y_valid)]}
    )
    model.fit(
        x_train, y_train, **validation_args,
        callbacks=[lgb.early_stopping(50, first_metric_only=True, verbose=True)],
    )
    training_seconds = perf_counter() - start
    probabilities = model.predict_proba(x_test, num_threads=args.threads)[:, 1]
    predictions = (probabilities >= 0.5).astype(np.int8)
    latency = timed_predictions(model, x_test.iloc[:1], 200, args.threads)
    batch = timed_predictions(model, x_test.iloc[:1000], 50, args.threads)
    hardware_type = instance_type()
    result = {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "source": "kaggle:mlg-ulb/creditcardfraud", "file": args.dataset.name,
            "sha256": sha256(args.dataset), "rows": len(frame),
            "features": features.shape[1], "fraud_rows": int(target.sum()),
            "train_rows": len(x_train), "validation_rows": len(x_valid),
            "test_rows": len(x_test), "test_fraud_rows": int(y_test.sum()),
        },
        "environment": {
            "ec2_instance_type": hardware_type,
            "platform": platform.platform(), "architecture": platform.machine(),
            "logical_cpus": os.cpu_count(), "threads_used": args.threads,
            "python": platform.python_version(), "lightgbm": lgb.__version__,
            "scikit_learn": sklearn.__version__, "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "method": {
            "random_seed": 42, "split": "stratified 64% train / 16% validation / 20% test",
            "early_stopping_metric": "validation average_precision",
            "early_stopping_rounds": 50, "decision_threshold": 0.5,
            "latency_repetitions": len(latency), "batch_repetitions": len(batch),
            "warmup_calls_per_measurement": 5, "batch_rows": 1000,
            "timing_scope": "in-process LGBMClassifier.predict_proba; excludes network and input preparation",
            "model_parameters": model.get_params(),
        },
        "load_data_seconds": load_seconds,
        "training_seconds": training_seconds,
        "best_iteration": int(model.best_iteration_),
        "auc_roc": float(roc_auc_score(y_test, probabilities)),
        "accuracy": float(accuracy_score(y_test, predictions)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "average_precision": float(average_precision_score(y_test, probabilities)),
        "majority_class_accuracy": float((y_test == 0).mean()),
        "confusion_matrix": confusion_matrix(y_test, predictions, labels=[0, 1]).tolist(),
        "inference_latency_ms": float(latency.mean() * 1000),
        "inference_latency_p50_ms": float(np.median(latency) * 1000),
        "inference_latency_p95_ms": float(np.percentile(latency, 95) * 1000),
        "inference_batch_seconds": float(batch.mean()),
        "inference_throughput_rows_per_second": float(1000 / batch.mean()),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    metrics = [
        ("Thời gian load data", f"{load_seconds:.4f} s"),
        ("Thời gian training", f"{training_seconds:.4f} s"),
        ("Best iteration", str(result["best_iteration"])),
        *((label, f"{result[key]:.6f}") for label, key in [
            ("AUC-ROC", "auc_roc"), ("Accuracy", "accuracy"), ("F1-Score", "f1_score"),
            ("Precision", "precision"), ("Recall", "recall"),
        ]),
        ("Inference latency (1 row)", f"{result['inference_latency_ms']:.4f} ms (mean, 200 calls)"),
        ("Inference throughput (1000 rows)", f"{result['inference_throughput_rows_per_second']:.2f} rows/s (mean batch: {batch.mean():.6f} s)"),
    ]
    table = "| Metric | Kết quả |\n|---|---|\n" + "".join(f"| {label} | {value} |\n" for label, value in metrics)
    args.output.with_name("benchmark_metrics.md").write_text(table, encoding="utf-8")
    report = [
        f"Benchmark được thực hiện trên EC2 {hardware_type} (CPU, {args.threads} luồng), LightGBM {lgb.__version__} và toàn bộ 284.807 giao dịch Kaggle.",
        "Dữ liệu được chia stratified thành 64% train, 16% validation và 20% test với seed 42; test không dùng cho early stopping.",
        f"Thời gian đọc CSV là {load_seconds:.4f} giây; training mất {training_seconds:.4f} giây với best iteration {model.best_iteration_}.",
        f"AUC-ROC trên test đạt {result['auc_roc']:.6f}; average precision đạt {result['average_precision']:.6f}.",
        f"Tại ngưỡng 0,5, Precision={result['precision']:.6f}, Recall={result['recall']:.6f}, F1={result['f1_score']:.6f}.",
        f"Accuracy={result['accuracy']:.6f}; cần đối chiếu baseline luôn đoán không gian lận ({result['majority_class_accuracy']:.6f}) vì dữ liệu mất cân bằng.",
        f"Latency trung bình cho một dòng là {result['inference_latency_ms']:.4f} ms, p95={result['inference_latency_p95_ms']:.4f} ms sau warmup.",
        f"Throughput batch 1.000 dòng đạt {result['inference_throughput_rows_per_second']:.2f} dòng/giây; phép đo chạy trong tiến trình Python, không bao gồm mạng/API.",
        "Các thời gian phản ánh lần chạy này; tải hệ thống và loại instance có thể làm kết quả các lần chạy khác thay đổi.",
    ]
    args.output.with_name("report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n" + table, flush=True)
    print(f"Average precision: {result['average_precision']:.6f}")
    print(f"Confusion matrix [[TN, FP], [FN, TP]]: {result['confusion_matrix']}")
    print(f"Saved: {args.output}, benchmark_metrics.md, report.md", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError) as error:
        print(f"Benchmark failed: {error}", file=sys.stderr)
        sys.exit(1)
