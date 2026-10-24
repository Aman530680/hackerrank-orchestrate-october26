import pandas as pd
import json, os

df_ev = pd.read_csv('dataset/evidence_files.csv')
sample_evs = ['evidence_01', 'evidence_03', 'evidence_05', 'evidence_51', 'evidence_54', 'evidence_56', 'evidence_57', 'evidence_58', 'evidence_59', 'evidence_61', 'evidence_92', 'evidence_93', 'evidence_94']
for _, row in df_ev[df_ev['file_id'].isin(sample_evs)].iterrows():
    full_path = os.path.join('dataset', row['file_path'])
    sz = os.path.getsize(full_path) if os.path.exists(full_path) else -1
    print(f"{row['file_id']} | {row['captured_at']} | size={sz} | {row['origin']} | {row['file_path']}")
