"""Export the WMT16 Romanian-English test set used in the lab (and in the gentlenlp reference notebook).

Reference notebook call:  load_dataset('wmt16', 'ro-en', split='test')
Current namespaced id:    load_dataset('wmt/wmt16', 'ro-en', split='test')   (same data, 1,999 pairs)

Usage:  python scripts/export_dataset.py
Writes: data/wmt16_ro-en_test.csv  and  data/wmt16_ro-en_test.jsonl
"""
import csv
import hashlib
import json
import pathlib

from datasets import load_dataset

OUT = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

ds = load_dataset("wmt/wmt16", "ro-en", split="test")
rows = [{"id": i, "en": r["translation"]["en"], "ro": r["translation"]["ro"]} for i, r in enumerate(ds)]
assert len(rows) == 1999, len(rows)

csv_path, jsonl_path = OUT / "wmt16_ro-en_test.csv", OUT / "wmt16_ro-en_test.jsonl"
with csv_path.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["id", "en", "ro"])
    w.writeheader()
    w.writerows(rows)
with jsonl_path.open("w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

for p in (csv_path, jsonl_path):
    print(f"{p.name}: {len(rows)} rows, sha256={hashlib.sha256(p.read_bytes()).hexdigest()[:16]}...")
print("dataset fingerprint (HF):", ds._fingerprint)
