import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

for idx, r in df_req.iterrows():
    cid = r['case_id']
    rep_t = r['reported_at_dt']
    out = df_out[df_out['case_id'] == cid].iloc[0]
    exp = json.loads(out['steps_json'])
    exp_res = set(s['resource_id'] for s in exp)
    
    # Check deletion_worker events within 1 hour before reported_at up to 10 minutes after
    sub = df_sys[(df_sys['event_time_dt'] >= rep_t - pd.Timedelta(hours=2)) & 
                 (df_sys['event_time_dt'] <= rep_t + pd.Timedelta(minutes=15)) &
                 (df_sys['source_system'] == 'deletion_worker')]
    
    matches = set(sub['resource_id']).intersection(exp_res)
    print(f"[{cid}] rep={r['reported_at']} exp_count={len(exp_res)} in_rep_window={len(matches)} / {len(exp_res)}")
