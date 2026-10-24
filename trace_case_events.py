import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Inspect case 25, 26, 27, 28, 29, 30
cases = ['case_25', 'case_26', 'case_27', 'case_28', 'case_29', 'case_30']
for cid in cases:
    req = df_req[df_req['case_id'] == cid].iloc[0]
    out = df_out[df_out['case_id'] == cid].iloc[0]
    exp = json.loads(out['steps_json'])
    exp_res = set(s['resource_id'] for s in exp)
    rep_time = req['reported_at_dt']
    
    # Let's see the exact events for this case's expected resources
    evs = df_sys[df_sys['resource_id'].isin(exp_res)]
    print(f"\n=== {cid} reported_at={req['reported_at']} ===")
    for _, e in evs.iterrows():
        print(f"  {e['activity_id']} | {e['event_time']} | {e['event_type']} | {e['source_system']}->{e['target_system']} | {e['resource_id']} | {e['reported_result']} | {e['details']}")
