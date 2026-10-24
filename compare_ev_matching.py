import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

for _, r in df_req.iterrows():
    cid = r['case_id']
    st = df_out[df_out['case_id'] == c if 'c' in locals() else df_out['case_id'] == cid]['deletion_status'].values[0]
    steps = json.loads(df_out[df_out['case_id'] == cid]['steps_json'].values[0])
    truth_evs = sorted(list(set(s['evidence_id'] for s in steps if s.get('evidence_id'))))
    audit_at = r['audit_at']
    
    # Check evidence files captured at or before audit_at
    prior_ev = df_ev[df_ev['captured_at'] <= audit_at].sort_values('captured_at', ascending=False)
    
    # Check which evidence files contain any resource from steps
    step_resources = set(s['resource_id'] for s in steps)
    matching_evs = set()
    for res in step_resources:
        m = df_parsed[df_parsed['resource_id'] == res]
        for fid in m['evidence_id'].unique():
            matching_evs.add(fid)
            
    print(f"{cid} | audit={audit_at} | truth_evs={truth_evs} | matching_evs={sorted(list(matching_evs))}")
