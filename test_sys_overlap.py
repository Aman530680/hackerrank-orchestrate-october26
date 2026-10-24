import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

for idx, req in df_req.iterrows():
    cid = req['case_id']
    rep_time = req['reported_at_dt']
    req_time = req['requested_at_dt']
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    expected_steps = json.loads(out_row['steps_json'])
    expected_resources = set(s['resource_id'] for s in expected_steps)
    
    # Let's find events by deletion_worker in window [rep_time - 24h, rep_time + 4h]
    # But wait, what if reported_status is NOT_STARTED?
    # For NOT_STARTED, reported_at is when the intake claimed NOT_STARTED!
    window = df_sys[(df_sys['event_time_dt'] >= req_time - pd.Timedelta(hours=2)) & 
                    (df_sys['event_time_dt'] <= rep_time + pd.Timedelta(hours=4)) &
                    (df_sys['source_system'] == 'deletion_worker')]
    
    window_res = set(window['resource_id'].dropna())
    
    # How many expected resources are in window_res?
    overlap = expected_resources.intersection(window_res)
    print(f"[{cid}] expected={len(expected_resources)} window={len(window_res)} overlap={len(overlap)}")
    if overlap != expected_resources:
        missing = expected_resources - overlap
        print(f"   Missing from deletion_worker window: {missing}")
