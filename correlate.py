import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])
df_req['audit_at_dt'] = pd.to_datetime(df_req['audit_at'])

for idx, req in df_req.head(10).iterrows():
    case_id = req['case_id']
    rep_time = req['reported_at_dt']
    req_time = req['requested_at_dt']
    out_row = df_out[df_out['case_id'] == case_id].iloc[0]
    steps = json.loads(out_row['steps_json'])
    res_ids_in_steps = [s['resource_id'] for s in steps]
    
    # Find events around reported_at or requested_at
    nearby = df_sys[(df_sys['event_time_dt'] >= req_time - pd.Timedelta(hours=2)) & 
                    (df_sys['event_time_dt'] <= rep_time + pd.Timedelta(hours=2))]
    
    print(f"=== {case_id} ({req['reported_status']}) requested={req['requested_at']} reported={req['reported_at']}")
    print(f"    Expected steps resources: {res_ids_in_steps}")
    # filter nearby that match res_ids
    matching = nearby[nearby['resource_id'].isin(res_ids_in_steps)]
    print(f"    Matching events count: {len(matching)}")
    for _, m in matching.iterrows():
        print(f"      {m['event_time']} | {m['event_type']} | {m['source_system']} -> {m['target_system']} | res={m['resource_id']} | res_res={m['reported_result']}")
