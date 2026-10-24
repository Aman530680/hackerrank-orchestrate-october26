import pandas as pd
import json, os, sys, re, sqlite3
from pypdf import PdfReader

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
df_rules = pd.read_csv('dataset/deletion_rules.csv')

# Build user mapping
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

# Load parsed evidence index
df_parsed = pd.read_pickle('dataset/parsed_evidence.pkl')

print("Loaded all data.")
