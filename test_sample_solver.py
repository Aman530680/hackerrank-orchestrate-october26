import pandas as pd
import json, sys, re, os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath('code/evaluation'))
import evaluate_samples

# Load files
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

print("Analyzing sample cases vs parsed evidence and system activity...")
for _, req in df_req.head(5).iterrows():
    cid = req['case_id']
    u = email_to_user[req['email'].lower()]
    u_emails = user_to_emails[u]
    audit_time = req['audit_at']
    truth_row = df_truth[df_truth['case_id'] == cid].iloc[0]
    t_status = truth_row['deletion_status']
    t_steps = json.loads(truth_row['steps_json'])
    
    # Check what records exist in df_parsed for u or u_emails up to audit_time
    ev_matches = df_parsed[((df_parsed['user_id'] == u) | (df_parsed['identifier'].str.lower().isin(u_emails))) &
                           (df_parsed['captured_at'] <= audit_time)]
    
    print(f"\n[{cid}] user={u} truth={t_status}")
    print(f"  Truth steps ({len(t_steps)}):")
    for s in t_steps:
        print(f"    [{s['phase']}] {s['system_id']} {s['resource_id']} {s['operation']} {s['state']} ev={s['evidence_id']}")
    print(f"  Evidence matches ({len(ev_matches)}):")
    for _, em in ev_matches.iterrows():
        print(f"    {em['evidence_id']} ({em['captured_at']}) {em['system_id']} {em['resource_id']} raw_st={em['raw_status']}")
