import pandas as pd
import json

df = pd.read_csv('dataset/sample_output.csv')
for _, r in df.iterrows():
    c = r['case_id']
    st = r['deletion_status']
    steps = json.loads(r['steps_json'])
    findings = [f"{s['system_id']}:{s['resource_id']}({s['operation']})" for s in steps if s['phase'] == 'FINDING']
    rems = [f"{s['system_id']}:{s['resource_id']}({s['operation']})" for s in steps if s['phase'] == 'REMEDIATION']
    verifs = [f"{s['system_id']}:{s['resource_id']}({s['operation']},{s['evidence_id']})" for s in steps if s['phase'] == 'VERIFICATION']
    print(f"{c:7} | {st:10} | F:{len(findings)} R:{len(rems)} V:{len(verifs)} | {findings}")
