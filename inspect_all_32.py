import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')

for _, r in df_req.iterrows():
    c = r['case_id']
    st = df_out[df_out['case_id'] == c]['deletion_status'].values[0]
    steps = json.loads(df_out[df_out['case_id'] == c]['steps_json'].values[0])
    evs = sorted(list(set(s['evidence_id'] for s in steps if s.get('evidence_id'))))
    res_list = [f"{s['system_id']}:{s['resource_id']}" for s in steps if s['phase'] == 'FINDING' or (st == 'COMPLETE' and s['phase'] == 'VERIFICATION')]
    print(f"{c} | status={st:10} | audit_at={r['audit_at']} | evs={evs} | items={res_list}")
