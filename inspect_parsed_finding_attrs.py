import pandas as pd
import json

df_out = pd.read_csv('dataset/sample_output.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

all_findings = []
for _, r in df_out.iterrows():
    c = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        if s['phase'] == 'FINDING':
            all_findings.append((c, s['system_id'], s['resource_id'], s['operation'], s['evidence_id']))

print(f"Total findings across sample output: {len(all_findings)}")
for c, sys_id, res_id, op, ev_id in all_findings:
    ev_rows = df_parsed[(df_parsed['evidence_id'] == ev_id) & (df_parsed['resource_id'] == res_id)]
    if len(ev_rows):
        er = ev_rows.iloc[0]
        print(f"[{c}] {sys_id} | {res_id} | {op} | ev={ev_id} | raw_st={er['raw_status']} | uid={er['user_id']} | raw_rec={str(er['raw_record'])[:100]}")
    else:
        print(f"[{c}] {sys_id} | {res_id} | {op} | ev={ev_id} | NOT IN DF_PARSED")
