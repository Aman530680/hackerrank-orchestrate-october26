import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')
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

print(f"Total sample cases: {len(df_req)}")

all_res_findings = []
for _, req in df_req.iterrows():
    cid = req['case_id']
    u = email_to_user[req['email'].lower()]
    u_emails = user_to_emails[u]
    audit_at = req['audit_at']
    out_row = df_out[df_out['case_id'] == cid].iloc[0]
    expected_steps = json.loads(out_row['steps_json'])
    
    for s in expected_steps:
        res = s['resource_id']
        sys_id = s['system_id']
        phase = s['phase']
        op = s['operation']
        st = s['state']
        ev = s['evidence_id']
        
        # Check parsed evidence
        ev_matches = df_parsed[df_parsed['resource_id'] == res]
        ev_sources = list(ev_matches['evidence_id'].unique())
        
        # Check system activity
        sys_matches = df_sys[df_sys['resource_id'] == res]
        sys_events = list(sys_matches['event_type'].unique())
        
        all_res_findings.append({
            'case_id': cid,
            'user_id': u,
            'phase': phase,
            'system_id': sys_id,
            'resource_id': res,
            'op': op,
            'state': st,
            'evidence_id': ev,
            'in_evidence': ev_sources,
            'in_system_activity': sys_events
        })

df_all = pd.DataFrame(all_res_findings)
print(f"Total steps analyzed: {len(df_all)}")
print(f"Steps with resource in parsed evidence: {df_all['in_evidence'].apply(lambda x: len(x) > 0).sum()} / {len(df_all)}")
print(f"Steps with resource in system activity: {df_all['in_system_activity'].apply(lambda x: len(x) > 0).sum()} / {len(df_all)}")
print(f"Steps with resource in EITHER: {((df_all['in_evidence'].apply(lambda x: len(x) > 0)) | (df_all['in_system_activity'].apply(lambda x: len(x) > 0))).sum()} / {len(df_all)}")

not_in_either = df_all[(df_all['in_evidence'].apply(lambda x: len(x) == 0)) & (df_all['in_system_activity'].apply(lambda x: len(x) == 0))]
print(f"\nNot in either ({len(not_in_either)}):")
print(not_in_either[['case_id', 'user_id', 'system_id', 'resource_id', 'op', 'evidence_id']].to_string())
