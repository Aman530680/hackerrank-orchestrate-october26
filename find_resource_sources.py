import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')

# Load build_evidence_db parsed records
from build_evidence_db import df_parsed

# Build email <-> user mapping
email_to_user = {}
user_to_emails = {}
for _, row in df_users.iterrows():
    u = row['user_id']
    e = str(row['email']).lower().strip()
    email_to_user[e] = u
    user_to_emails.setdefault(u, set()).add(e)

for _, row in df_audit[df_audit['field_name'] == 'email'].iterrows():
    u = row['user_id']
    old_e = str(row['old_value']).lower().strip()
    new_e = str(row['new_value']).lower().strip()
    email_to_user[old_e] = u
    email_to_user[new_e] = u
    user_to_emails.setdefault(u, set()).add(old_e)
    user_to_emails.setdefault(u, set()).add(new_e)

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Check for each sample case
all_found = 0
total_res = 0

for _, req in df_req.iterrows():
    cid = req['case_id']
    req_time = req['requested_at_dt']
    rep_time = req['reported_at_dt']
    u = email_to_user[req['email'].lower()]
    u_emails = user_to_emails[u]
    
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    expected_steps = json.loads(out_row['steps_json'])
    exp_res = set(s['resource_id'] for s in expected_steps)
    total_res += len(exp_res)
    
    # 1. Candidate resources from system_activity:
    # deletion_worker events in [req_time - 2h, rep_time + 4h]
    # But notice: multiple deletion_worker events can happen in that window.
    # Can we match resources that also appear in evidence for this user or email?
    
    # Candidate resources from evidence:
    ev_for_user = df_parsed[(df_parsed['user_id'] == u) | 
                            (df_parsed['identifier'].str.lower().isin(u_emails))]
    ev_res = set(ev_for_user['resource_id'].dropna())
    
    # Candidate resources from system_activity window
    sys_window = df_sys[(df_sys['event_time_dt'] >= req_time - pd.Timedelta(hours=2)) & 
                        (df_sys['event_time_dt'] <= rep_time + pd.Timedelta(hours=4)) &
                        (df_sys['source_system'] == 'deletion_worker')]
    sys_res = set(sys_window['resource_id'].dropna())
    
    # Also check if any system_activity details mention u or u_emails
    sys_direct = df_sys[df_sys['details'].apply(lambda d: any(em in str(d).lower() for em in u_emails) or u in str(d))]
    sys_direct_res = set(sys_direct['resource_id'].dropna())
    
    combined = ev_res.union(sys_direct_res)
    # If a resource from sys_res is also in evidence for this user, it's definitely this user's resource
    # What about account_xxxx?
    # Notice: In sys_window, which account_xxxx belongs to this user?
    
    print(f"[{cid}] user={u} exp={exp_res}")
    print(f"    ev_res={ev_res}")
    print(f"    sys_window_accounts={[r for r in sys_res if r.startswith('account_')]}")
