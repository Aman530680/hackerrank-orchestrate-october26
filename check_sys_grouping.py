import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Let's inspect cases 25 to 32
for cid in ['case_25', 'case_26', 'case_27', 'case_28', 'case_29', 'case_30', 'case_31', 'case_32']:
    r = df_req[df_req['case_id'] == cid].iloc[0]
    out = df_out[df_out['case_id'] == cid].iloc[0]
    exp = json.loads(out['steps_json'])
    exp_res = [s['resource_id'] for s in exp]
    print(f"\n{cid} | rep={r['reported_at']} | res={exp_res}")
    
    # Check all events in system_activity for these resources
    for res in set(exp_res):
        evs = df_sys[df_sys['resource_id'] == res]
        for _, e in evs.iterrows():
            print(f"  {res:16} | {e['event_time']} | {e['event_type']} | {e['source_system']}->{e['target_system']} | res_res={e['reported_result']}")
