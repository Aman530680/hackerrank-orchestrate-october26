import os, sys, json, re
import pandas as pd

# Load files
df_req = pd.read_csv('dataset/deletion_requests.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

# User mappings
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

# Catalog link mappings from system activity
catalog_links = {}
for _, row in df_sys[df_sys['event_type'] == 'LINK_RESOURCE_IDENTITY'].iterrows():
    res_id = row['resource_id']
    det = row['details']
    m_user = re.findall(r'user_[0-9]+', det)
    m_email = re.findall(r'[\w\.-]+@[\w\.-]+', det)
    uid = m_user[0] if m_user else (email_to_user.get(m_email[0].lower()) if m_email else None)
    if uid:
        catalog_links[res_id] = uid

NON_DEL_PHRASES = [
    'leave the account active', 'not asking for deletion', 'keep the account as it is',
    'do not close the account', 'without removing any of my records',
    'remove me from marketing lists only', 'not a request to erase it',
    'leave my profile and purchase history in place', 'continue using the service',
    "please don't delete or change anything", 'not asking to delete', 'keep my account'
]

def is_deletion_request(text):
    if not text or pd.isna(text):
        return True
    t = str(text).lower()
    for phrase in NON_DEL_PHRASES:
        if phrase in t:
            return False
    return True

df_sys['event_time_dt'] = pd.to_datetime(df_sys['event_time'])
df_req['requested_at_dt'] = pd.to_datetime(df_req['requested_at'])
df_req['reported_at_dt'] = pd.to_datetime(df_req['reported_at'])

# Check distribution of requests
na_cases = []
del_cases = []
for _, r in df_req.iterrows():
    if not is_deletion_request(r['request_text']):
        na_cases.append(r['case_id'])
    else:
        del_cases.append(r['case_id'])

print(f"Total cases: {len(df_req)}")
print(f"NOT_APPLICABLE cases ({len(na_cases)}): {na_cases}")
print(f"Deletion cases ({len(del_cases)})")
