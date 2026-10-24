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

print(f"Total mapped emails: {len(email_to_user)}, Total users: {len(user_to_emails)}")

# For each sample case, let's look at all resources in system_activity
for _, req in df_req.iterrows():
    cid = req['case_id']
    email = req['email'].lower()
    u = email_to_user.get(email)
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    expected_steps = json.loads(out_row['steps_json'])
    
    # Check what resources appear in expected_steps
    exp_res = [s['resource_id'] for s in expected_steps]
    
    # Check what resources in system_activity mention this user or these resources
    sys_matches = df_sys[df_sys['resource_id'].isin(exp_res)]
    
    print(f"\n--- {cid} (user={u}) status={out_row['deletion_status']} rep_status={req['reported_status']} ---")
    print(f"  Expected resources: {exp_res}")
    print(f"  Matched {len(sys_matches)} events in system_activity for expected resources:")
    for _, sm in sys_matches.iterrows():
        print(f"    ev_id={sm['activity_id']} time={sm['event_time']} type={sm['event_type']} {sm['source_system']}->{sm['target_system']} res={sm['resource_id']} res_res={sm['reported_result']}")
