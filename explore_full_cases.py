import pandas as pd
import json, re

df_req = pd.read_csv('dataset/deletion_requests.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

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

for idx in range(10):
    r = df_req.iloc[idx]
    cid = r['case_id']
    u = email_to_user[r['email'].lower().strip()]
    u_emails = user_to_emails[u]
    rep_t = r['reported_at_dt']
    req_t = r['requested_at_dt']
    audit_at = r['audit_at']
    rep_status = r['reported_status']
    
    # 1. Evidence matches for this user
    ev_m = df_parsed[((df_parsed['user_id'] == u) | 
                     (df_parsed['identifier'].str.lower().isin(u_emails))) &
                    (df_parsed['captured_at'] <= audit_at)]
    ev_res = set(ev_m['resource_id'].dropna())
    
    # 2. System activity around reported_at
    sys_m = df_sys[(df_sys['event_time_dt'] >= rep_t - pd.Timedelta(hours=2)) & 
                   (df_sys['event_time_dt'] <= rep_t + pd.Timedelta(minutes=15)) &
                   (df_sys['source_system'] == 'deletion_worker')]
    sys_res = set(sys_m['resource_id'].dropna())
    
    print(f"\n[{cid}] user={u} rep_status={rep_status} rep_at={r['reported_at']} audit_at={audit_at}")
    print(f"  Evidence resources ({len(ev_res)}): {ev_res}")
    print(f"  System resources around reported_at ({len(sys_res)}): {sys_res}")
