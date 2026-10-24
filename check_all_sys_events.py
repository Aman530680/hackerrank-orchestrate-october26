import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_del = pd.read_csv('dataset/deletion_requests.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')

# Build mapping
email_to_user = {}
for _, row in df_users.iterrows():
    u = row['user_id']
    e = str(row['email']).lower().strip()
    email_to_user[e] = u

for _, row in df_audit[df_audit['field_name'] == 'email'].iterrows():
    u = row['user_id']
    email_to_user[str(row['old_value']).lower().strip()] = u
    email_to_user[str(row['new_value']).lower().strip()] = u

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_del['requested_at_dt'] = pd.to_datetime(df_del['requested_at'])
df_del['reported_at_dt'] = pd.to_datetime(df_del['reported_at'])

# Check for each case if there are deletion_worker events
cases_with_events = 0
cases_without_events = []

for _, r in df_del.iterrows():
    cid = r['case_id']
    rep_time = r['reported_at_dt']
    req_time = r['requested_at_dt']
    
    # Check deletion worker events in window [req_time - 1h, rep_time + 1h]
    window = df_sys[(df_sys['event_time_dt'] >= req_time - pd.Timedelta(hours=1)) &
                    (df_sys['event_time_dt'] <= rep_time + pd.Timedelta(hours=1)) &
                    (df_sys['source_system'] == 'deletion_worker')]
    if len(window) > 0:
        cases_with_events += 1
    else:
        cases_without_events.append((cid, r['reported_status'], r['request_text'][:60]))

print(f"Total deletion requests: {len(df_del)}")
print(f"Cases with deletion_worker events in window: {cases_with_events}")
print(f"Cases without events: {len(cases_without_events)}")
if cases_without_events:
    print("Samples without events:")
    for c in cases_without_events[:15]:
        print(" ", c)
