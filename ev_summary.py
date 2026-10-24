import pandas as pd
import os

df_ev = pd.read_csv('dataset/evidence_files.csv')
exts = {}
for _, row in df_ev.iterrows():
    p = row['file_path']
    ext = os.path.splitext(p)[1]
    exts[ext] = exts.get(ext, 0) + 1

print("Evidence file types count:")
for ext, count in sorted(exts.items()):
    print(f"  {ext}: {count}")

print("\nOrigins count:")
print(df_ev['origin'].value_counts())
