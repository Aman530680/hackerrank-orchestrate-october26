import pandas as pd
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')

# Build mapping from email -> user_id
email_to_user = {}
user_to_emails = {}
for _, row in df_users.iterrows():
    u = row['user_id']
    e = str(row['email']).lower()
    email_to_user[e] = u
    user_to_emails.setdefault(u, set()).add(e)

for _, row in df_audit[df_audit['field_name'] == 'email'].iterrows():
    u = row['user_id']
    old_e = str(row['old_value']).lower()
    new_e = str(row['new_value']).lower()
    email_to_user[old_e] = u
    email_to_user[new_e] = u
    user_to_emails.setdefault(u, set()).add(old_e)
    user_to_emails.setdefault(u, set()).add(new_e)

# Let's inspect where each resource in expected steps appears in evidence and system_activity
for _, req in df_req.iterrows():
    cid = req['case_id']
    email = req['email'].lower()
    uid = email_to_user.get(email)
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    steps = json.loads(out_row['steps_json'])
    
    print(f"\n==================== {cid} | {req['reported_status']} -> {out_row['deletion_status']} | user={uid} ====================")
    print(f"audit_at={req['audit_at']}")
    for s in steps:
        res = s['resource_id']
        sys_id = s['system_id']
        op = s['operation']
        ev_id = s['evidence_id']
        phase = s['phase']
        
        # Check in system activity
        sys_acts = df_sys[df_sys['resource_id'] == res]
        act_info = []
        for _, sa in sys_acts.iterrows():
            act_info.append(f"{sa['event_type']}:{sa['reported_result']}@{sa['event_time']}")
        
        print(f"  [{phase}] {sys_id} | {res} | {op} | {s['state']} | ev={ev_id} | sys_act={'; '.join(act_info)}")
