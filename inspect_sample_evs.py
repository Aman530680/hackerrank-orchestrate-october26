import pandas as pd
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

# Let's inspect evidence_01, evidence_05, evidence_94, evidence_51
files_to_check = ['evidence_01', 'evidence_05', 'evidence_51', 'evidence_94']
df_ev = pd.read_csv('dataset/evidence_files.csv')

for fid in files_to_check:
    row = df_ev[df_ev['file_id'] == fid].iloc[0]
    path = os.path.join('dataset', row['file_path'])
    print(f"\n=================== {fid} ({row['origin']}) {row['captured_at']} ===================")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    print("Length:", len(content))
    print(content[:600])
