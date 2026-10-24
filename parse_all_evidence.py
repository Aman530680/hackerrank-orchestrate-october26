import pandas as pd
import json, os, sys, re

sys.stdout.reconfigure(encoding='utf-8')

df_ev = pd.read_csv('dataset/evidence_files.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
df_del = pd.read_csv('dataset/deletion_requests.csv')

# Build mapping of all emails and users
all_users = set(df_users['user_id'])
all_emails = set(df_users['email'].str.lower())
for _, r in df_audit[df_audit['field_name'] == 'email'].iterrows():
    all_emails.add(str(r['old_value']).lower())
    all_emails.add(str(r['new_value']).lower())

print(f"Total users: {len(all_users)}, Total known emails: {len(all_emails)}")

# For each evidence file, see what it matches
evidence_findings = []
for _, row in df_ev.iterrows():
    fid = row['file_id']
    fpath = os.path.join('dataset', row['file_path'])
    ext = os.path.splitext(fpath)[1].lower()
    if not os.path.exists(fpath):
        continue
    
    # Read text
    if ext in ['.json', '.txt', '.log', '.sql']:
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            txt = f.read()
        
        # Check matched users / emails
        matched_u = [u for u in all_users if u in txt]
        matched_e = [e for e in all_emails if e in txt.lower()]
        
        # Check resource pattern: (account|analytics|support|search|data_flow|backup|audit_record|export|tombstone)_[0-9]+
        res_matches = set(re.findall(r'\b(?:account|analytics|support|search|data_flow|backup|audit_record|export|tombstone)_[0-9]+\b', txt))
        
        evidence_findings.append({
            'file_id': fid,
            'ext': ext,
            'origin': row['origin'],
            'captured_at': row['captured_at'],
            'matched_users': len(matched_u),
            'matched_emails': len(matched_e),
            'resource_count': len(res_matches),
            'sample_resources': list(res_matches)[:5]
        })

df_findings = pd.DataFrame(evidence_findings)
print("Evidence analysis summary:")
print(df_findings[['file_id', 'ext', 'captured_at', 'matched_users', 'matched_emails', 'resource_count']].to_string())
