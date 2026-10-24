import pandas as pd
import json, re, os, sys

sys.stdout.reconfigure(encoding='utf-8')

df_del = pd.read_csv('dataset/deletion_requests.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')

# Build mapping
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

print("Starting resource discovery test...")

# For each request, let's find events in system_activity
# How does system_activity correlate to requests?
# Earlier we noticed:
# In system_activity, events by deletion_worker occur around reported_at or requested_at!
# Let's check the timing!

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_del['requested_at_dt'] = pd.to_datetime(df_del['requested_at'])
df_del['reported_at_dt'] = pd.to_datetime(df_del['reported_at'])

# Check for a few cases
for idx in range(5):
    req = df_del.iloc[idx]
    cid = req['case_id']
    email = req['email'].lower()
    uid = email_to_user[email]
    req_time = req['requested_at_dt']
    rep_time = req['reported_at_dt']
    
    # window: [req_time, rep_time + 1 hour]
    window_events = df_sys[(df_sys['event_time_dt'] >= req_time - pd.Timedelta(hours=1)) &
                           (df_sys['event_time_dt'] <= rep_time + pd.Timedelta(hours=1))]
    print(f"\n[{cid}] user={uid} email={email} req={req['requested_at']} rep={req['reported_at']} ({len(window_events)} events in window)")
    print(window_events[['activity_id', 'event_time', 'event_type', 'source_system', 'target_system', 'resource_id', 'reported_result']])
