import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')

merged = pd.merge(df_req, df_out, on='case_id')

print("=== COMPLETE CASES ANALYSIS ===")
for _, r in merged[merged['deletion_status'] == 'COMPLETE'].iterrows():
    steps = json.loads(r['steps_json'])
    print(f"\n{r['case_id']}: rep_status={r['reported_status']}")
    for s in steps:
        print(f"  [{s['phase']}] {s['system_id']} | {s['resource_id']} | {s['operation']} | {s['state']} | ev={s['evidence_id']}")

print("\n\n=== INCOMPLETE CASES ANALYSIS (first 6) ===")
for _, r in merged[merged['deletion_status'] == 'INCOMPLETE'].head(6).iterrows():
    steps = json.loads(r['steps_json'])
    print(f"\n{r['case_id']}: rep_status={r['reported_status']}")
    for s in steps:
        print(f"  [{s['phase']}] {s['system_id']} | {s['resource_id']} | {s['operation']} | {s['state']} | ev={s['evidence_id']}")
