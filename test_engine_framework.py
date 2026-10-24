import pandas as pd
import json, os, sys, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('code/evaluation'))
import evaluate_samples

# Load datasets
df_samples = pd.read_csv('dataset/sample_deletion_requests.csv')
df_truth = pd.read_csv('dataset/sample_output.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

# User mapping
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
    # find user_xx
    m_user = re.findall(r'user_[0-9]+', det)
    m_email = re.findall(r'[\w\.-]+@[\w\.-]+', det)
    uid = m_user[0] if m_user else (email_to_user.get(m_email[0].lower()) if m_email else None)
    if uid:
        catalog_links[res_id] = uid

OP_ORDER = {
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}
PHASE_ORDER = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}

def sort_and_renumber(steps):
    def sort_key(s):
        return (PHASE_ORDER[s['phase']], OP_ORDER[s['operation']], s['system_id'], s['resource_id'])
    sorted_steps = sorted(steps, key=sort_key)
    for idx, s in enumerate(sorted_steps, 1):
        s['step_no'] = idx
    return sorted_steps

non_del_phrases = [
    'leave the account active', 'not asking for deletion', 'keep the account as it is',
    'do not close the account', 'without removing any of my records',
    'remove me from marketing lists only', 'not a request to erase it',
    'leave my profile and purchase history in place', 'continue using the service',
    'please don\'t delete or change anything', 'not asking to delete', 'keep my account'
]

def is_deletion_request(text):
    t = text.lower()
    for phrase in non_del_phrases:
        if phrase in t:
            return False
    return True

print("Ready to test.")
