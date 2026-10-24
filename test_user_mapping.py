import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df_del = pd.read_csv('dataset/deletion_requests.csv')
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
    old_e = str(row['old_value']).lower().strip()
    new_e = str(row['new_value']).lower().strip()
    email_to_user[old_e] = u
    email_to_user[new_e] = u

unmapped = []
for _, row in df_del.iterrows():
    cid = row['case_id']
    e = str(row['email']).lower().strip()
    if e not in email_to_user:
        unmapped.append((cid, e))

print(f"Total requests: {len(df_del)}")
print(f"Mapped: {len(df_del) - len(unmapped)}")
print(f"Unmapped count: {len(unmapped)}")
if unmapped:
    print("Unmapped samples:", unmapped[:10])
