#!/usr/bin/env python3
"""Try the official public Kaggle download without entering credentials."""

import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path


def main():
    output = Path("creditcard.csv")
    if output.exists():
        print("creditcard.csv already exists; keeping the existing file.")
        return
    url = "https://www.kaggle.com/api/v1/datasets/download/mlg-ulb/creditcardfraud"
    print("Trying the official Kaggle public dataset URL (no credentials).", flush=True)
    request = urllib.request.Request(url, headers={"User-Agent": "lab16-benchmark/1.0"})
    with tempfile.TemporaryFile() as archive:
        with urllib.request.urlopen(request, timeout=30) as response:
            shutil.copyfileobj(response, archive)
        archive.seek(0)
        with zipfile.ZipFile(archive) as dataset:
            members = [item for item in dataset.infolist() if Path(item.filename).name == "creditcard.csv"]
            if len(members) != 1:
                raise ValueError("Kaggle download did not contain exactly one creditcard.csv.")
            # Extract only the expected CSV, without trusting archive paths.
            with dataset.open(members[0]) as source, output.open("xb") as destination:
                shutil.copyfileobj(source, destination)
    print(f"Downloaded {output}: {output.stat().st_size:,} bytes.", flush=True)


if __name__ == "__main__":
    try:
        main()
    except (urllib.error.URLError, zipfile.BadZipFile, ValueError, OSError) as error:
        print(f"Public download unavailable: {error}. Complete step 4.3 manually.", file=sys.stderr)
        sys.exit(1)
