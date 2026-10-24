import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

for _, req in df_req.iterrows():
    cid = req['case_id']
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    expected_steps = json.loads(out_row['steps_json'])
    audits = [s['resource_id'] for s in expected_steps if s['system_id'] == 'security_service']
    for a in audits:
        m = df_parsed[df_parsed['resource_id'] == a]
        if len(m):
            print(f"{cid} -> {a}: in df_parsed (ev={m.iloc[0]['evidence_id']}, uid={m.iloc[0]['user_id']}, ident={m.iloc[0]['identifier']})")
        else:
            print(f"{cid} -> {a}: NOT in df_parsed")
