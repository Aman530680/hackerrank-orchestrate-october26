import pandas as pd
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')
df_ev = pd.read_csv('dataset/evidence_files.csv')

print(f"Total evidence files: {len(df_ev)}")

for idx, row in df_ev.iterrows():
    fid = row['file_id']
    fpath = os.path.join('dataset', row['file_path'])
    origin = row['origin']
    cap = row['captured_at']
    ext = os.path.splitext(fpath)[1].lower()
    sz = os.path.getsize(fpath) if os.path.exists(fpath) else -1
    
    # Check sample content
    sample = ""
    if ext in ['.json', '.txt', '.log', '.sql']:
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                head = f.read(300).replace('\n', ' ')
                sample = head[:150]
        except Exception as e:
            sample = f"Error: {e}"
    else:
        sample = f"Binary ({ext})"
    
    print(f"{fid:12} | {cap} | {ext:5} | {sz:7} bytes | {origin:35} | {sample}")
