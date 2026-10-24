import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Look at details of all deletion_worker events
for idx in range(10):
    r = df_req.iloc[idx]
    cid = r['case_id']
    req_t = r['requested_at_dt']
    rep_t = r['reported_at_dt']
    out = df_out[df_out['case_id'] == cid].iloc[0]
    exp = json.loads(out['steps_json'])
    exp_res = set(s['resource_id'] for s in exp)
    
    # Events in [req_t - 2h, rep_t + 2h]
    sub = df_sys[(df_sys['event_time_dt'] >= req_t - pd.Timedelta(hours=2)) & 
                 (df_sys['event_time_dt'] <= rep_t + pd.Timedelta(hours=2)) &
                 (df_sys['source_system'] == 'deletion_worker')]
    
    print(f"\n[{cid}] req={r['requested_at']} rep={r['reported_at']} exp_res={exp_res}")
    for _, e in sub.iterrows():
        is_exp = e['resource_id'] in exp_res
        marker = "===> MATCH" if is_exp else "          "
        print(f" {marker} | {e['event_time']} | {e['event_type']} | {e['target_system']} | {e['resource_id']} | {e['reported_result']} | {e['details'][:60]}")
