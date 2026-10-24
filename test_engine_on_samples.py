import pandas as pd
import json, sys, os, re

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('code/evaluation'))
import evaluate_samples

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_truth = pd.read_csv('dataset/sample_output.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')
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

# Non-deletion phrases
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

print("Checking sample cases...")
# For each sample case, let's see which evidence files are relevant
for _, req in df_req.iterrows():
    cid = req['case_id']
    u = email_to_user[req['email'].lower()]
    u_emails = user_to_emails[u]
    audit_at = req['audit_at']
    truth_row = df_truth[df_truth['case_id'] == cid].iloc[0]
    t_status = truth_row['deletion_status']
    t_steps = json.loads(truth_row['steps_json'])
    
    # Evidence files that have records for this user at or before audit_at
    user_ev = df_parsed[((df_parsed['user_id'] == u) | 
                         (df_parsed['identifier'].str.lower().isin(u_emails))) &
                        (df_parsed['captured_at'] <= audit_at)]
    ev_ids = user_ev['evidence_id'].unique()
    t_evs = set(s['evidence_id'] for s in t_steps if s.get('evidence_id'))
    
    print(f"[{cid}] user={u} truth={t_status:10} | found_evs={list(ev_ids)} | truth_evs={list(t_evs)}")
