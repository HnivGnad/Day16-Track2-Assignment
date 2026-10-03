#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -u benchmark.py "$@" 2>&1 | tee benchmark_output.txt
{
    date -u
    printf '\n=== CPU / processes (post-benchmark snapshot) ===\n'
    top -b -n 1 | head -n 20 || true
    printf '\n=== RAM ===\n'
    free -h
    printf '\n=== Network counters ===\n'
    ip -s link
} | tee resource_usage.txt
