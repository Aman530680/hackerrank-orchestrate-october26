import pandas as pd
import os, sys

sys.stdout.reconfigure(encoding='utf-8')
df_ev = pd.read_csv('dataset/evidence_files.csv')

for idx in range(0, 63):
    row = df_ev.iloc[idx]
    fid = row['file_id']
    fpath = os.path.join('dataset', row['file_path'])
    origin = row['origin']
    cap = row['captured_at']
    ext = os.path.splitext(fpath)[1].lower()
    sz = os.path.getsize(fpath) if os.path.exists(fpath) else -1
    print(f"{fid:12} | {cap} | {ext:5} | {sz:7} bytes | {origin:40} | {row['file_path']}")
