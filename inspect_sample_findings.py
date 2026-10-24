import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')

for _, r in df_req.iterrows():
    c = r['case_id']
    out = df_out[df_out['case_id'] == c].iloc[0]
    st = out['deletion_status']
    steps = json.loads(out['steps_json'])
    findings = [s for s in steps if s['phase'] == 'FINDING']
    
    if st == 'INCOMPLETE':
        f_info = []
        for f in findings:
            ev_id = f['evidence_id']
            ev_row = df_ev[df_ev['file_id'] == ev_id].iloc[0]
            f_info.append(f"{f['system_id']}:{f['resource_id']}:{f['operation']} in {ev_id}({ev_row['origin']})")
        print(f"[{c}] audit_at={r['audit_at']} | findings={len(findings)}: {'; '.join(f_info)}")
