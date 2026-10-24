import pandas as pd
import json

df_req = pd.read_csv('dataset/deletion_requests.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
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

print(f"Total deletion requests: {len(df_req)}")

# Check user resolution
unresolved = []
for _, req in df_req.iterrows():
    e = req['email'].lower().strip()
    if e not in email_to_user:
        unresolved.append((req['case_id'], e))

print(f"Unresolved emails: {len(unresolved)}")

# Check timing of deletion requests vs system activity
df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Check how many cases have events in system activity or evidence
has_sys = 0
has_ev = 0
has_either = 0

for _, req in df_req.iterrows():
    cid = req['case_id']
    u = email_to_user[req['email'].lower().strip()]
    u_emails = user_to_emails[u]
    audit_at = req['audit_at']
    
    # Evidence for user
    ev_m = df_parsed[((df_parsed['user_id'] == u) | (df_parsed['identifier'].str.lower().isin(u_emails))) & (df_parsed['captured_at'] <= audit_at)]
    
    # System events around requested/reported
    sys_m = df_sys[(df_sys['event_time_dt'] >= req['requested_at_dt'] - pd.Timedelta(hours=2)) & 
                   (df_sys['event_time_dt'] <= req['reported_at_dt'] + pd.Timedelta(hours=4))]
    
    if len(ev_m) > 0:
        has_ev += 1
    if len(sys_m) > 0:
        has_sys += 1
    if len(ev_m) > 0 or len(sys_m) > 0:
        has_either += 1

print(f"Cases with evidence matches: {has_ev} / {len(df_req)}")
print(f"Cases with system activity in window: {has_sys} / {len(df_req)}")
print(f"Cases with either: {has_either} / {len(df_req)}")
