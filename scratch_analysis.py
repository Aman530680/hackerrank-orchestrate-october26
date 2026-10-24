import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')

# Build mapping from email -> user_id
email_to_user = {}
for _, row in df_users.iterrows():
    email_to_user[row['email'].lower()] = row['user_id']
for _, row in df_audit[df_audit['field_name'] == 'email'].iterrows():
    email_to_user[row['old_value'].lower()] = row['user_id']
    email_to_user[row['new_value'].lower()] = row['user_id']

merged = pd.merge(df_req, df_out, on='case_id')
for idx, row in merged.iterrows():
    steps = json.loads(row['steps_json'])
    uid = email_to_user.get(row['email'].lower(), 'UNKNOWN')
    print(f"=== {row['case_id']}: status={row['deletion_status']} (user={uid}) email={row['email']} reported={row['reported_status']}")
    print(f"    text: {row['request_text'][:100]}")
    for s in steps:
        print(f"      step {s.get('step_no')}: [{s.get('phase')}] sys={s.get('system_id')} res={s.get('resource_id')} op={s.get('operation')} st={s.get('state')} ev={s.get('evidence_id')}")
