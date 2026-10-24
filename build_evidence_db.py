import json, os, sys, re, sqlite3
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

df_ev = pd.read_csv('dataset/evidence_files.csv')
df_users = pd.read_csv('dataset/user_identities.csv')
df_audit = pd.read_csv('dataset/user_audit_log.csv')

# Build mapping of emails <-> user_id
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

def resolve_user(email=None, user_id=None):
    if user_id and user_id in user_to_emails:
        return user_id
    if email:
        clean = email.lower().strip()
        if clean in email_to_user:
            return email_to_user[clean]
    return user_id

KV_PATTERN = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))')

parsed_records = []

for _, ev_row in df_ev.iterrows():
    fid = ev_row['file_id']
    fpath = os.path.join('dataset', ev_row['file_path'])
    cap = ev_row['captured_at']
    origin = ev_row['origin']
    ext = os.path.splitext(fpath)[1].lower()
    
    if not os.path.exists(fpath):
        continue
        
    # 1. TXT handover
    if ext == '.txt':
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line.startswith('-'):
                    continue
                parts = [p.strip() for p in line.lstrip('-').split('|')]
                if len(parts) >= 6:
                    t, sys_id, res_id, cat, raw_st, ident = parts[:6]
                    u = resolve_user(email=ident if '@' in ident else None, user_id=ident if ident.startswith('user_') else None)
                    parsed_records.append({
                        'evidence_id': fid,
                        'captured_at': cap,
                        'system_id': sys_id,
                        'resource_id': res_id,
                        'data_category': cat,
                        'raw_status': raw_st,
                        'identifier': ident,
                        'user_id': u,
                        'origin': origin
                    })

    # 2. JSON
    elif ext == '.json':
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            # Type A: service_resource_export
            if 'service_exports' in data:
                for sys_id, sys_data in data['service_exports'].items():
                    for coll_name, coll_items in sys_data.items():
                        for item in coll_items:
                            res_id = item.get('resource_id')
                            email = item.get('email') or item.get('customer_email') or item.get('owner_email') or item.get('requester_email')
                            user_ref = item.get('customer_reference') or item.get('subject_reference')
                            u = resolve_user(email=email, user_id=user_ref)
                            parsed_records.append({
                                'evidence_id': fid,
                                'captured_at': cap,
                                'system_id': sys_id,
                                'resource_id': res_id,
                                'data_category': coll_name,
                                'raw_status': item.get('status_code') or item.get('last_delivery_status') or ('ACTIVE' if item.get('enabled') else ('DISABLED' if item.get('enabled') is False else None)),
                                'identifier': email or user_ref,
                                'user_id': u,
                                'origin': origin,
                                'details': item
                            })
                            
            # Type B: records_assurance_snapshot_bundle
            elif 'snapshots' in data:
                for snap in data['snapshots']:
                    sys_id = snap.get('data_store')
                    coll = snap.get('collection')
                    for item in snap.get('records', []):
                        res_id = item.get('resource_id')
                        email = item.get('email')
                        if not email and isinstance(item.get('document'), dict):
                            email = item['document'].get('email')
                        user_ref = item.get('customer_reference') or item.get('subject_reference')
                        u = resolve_user(email=email, user_id=user_ref)
                        parsed_records.append({
                            'evidence_id': fid,
                            'captured_at': cap,
                            'system_id': sys_id,
                            'resource_id': res_id,
                            'data_category': coll,
                            'raw_status': item.get('account_status'),
                            'identifier': email or user_ref,
                            'user_id': u,
                            'origin': origin,
                            'details': item
                        })
                        
            # Type C: export_manifest or security_audit_ledger
            elif 'export_jobs' in data or 'exports' in data:
                jobs = data.get('export_jobs') or data.get('exports', [])
                for item in jobs:
                    res_id = item.get('resource_id') or item.get('job_id')
                    email = item.get('owner_email') or item.get('email')
                    u = resolve_user(email=email)
                    parsed_records.append({
                        'evidence_id': fid,
                        'captured_at': cap,
                        'system_id': 'export_service',
                        'resource_id': res_id,
                        'data_category': 'USER_EXPORT',
                        'raw_status': item.get('status'),
                        'identifier': email,
                        'user_id': u,
                        'origin': origin,
                        'details': item
                    })
            elif 'audit_records' in data:
                for item in data['audit_records']:
                    res_id = item.get('resource_id')
                    u = resolve_user(user_id=item.get('subject_reference'))
                    parsed_records.append({
                        'evidence_id': fid,
                        'captured_at': cap,
                        'system_id': 'security_service',
                        'resource_id': res_id,
                        'data_category': 'SECURITY_AUDIT_LOG',
                        'raw_status': 'RETAIN',
                        'identifier': item.get('subject_reference'),
                        'user_id': u,
                        'origin': origin,
                        'details': item
                    })
        except Exception as e:
            pass

    # 3. SQL SQLite
    elif ext == '.sql':
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                sql_text = f.read()
            conn = sqlite3.connect(':memory:')
            try:
                conn.executescript(sql_text)
                tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
                for t in tables:
                    if t == 'snapshot_scope':
                        continue
                    cursor = conn.execute(f"PRAGMA table_info({t})")
                    cols = [c[1] for c in cursor.fetchall()]
                    rows = conn.execute(f"SELECT * FROM {t}").fetchall()
                    for r in rows:
                        rd = dict(zip(cols, r))
                        res_id = rd.get('resource_id')
                        email = rd.get('email')
                        user_ref = rd.get('customer_reference') or rd.get('user_id')
                        u = resolve_user(email=email, user_id=user_ref)
                        
                        # Guess system_id from table name or origin
                        sys_id = 'account_service'
                        if 'search' in t:
                            sys_id = 'search_service'
                        elif 'analytics' in t:
                            sys_id = 'analytics_platform'
                        elif 'support' in t:
                            sys_id = 'support_platform'
                        elif 'export' in t:
                            sys_id = 'export_service'
                        elif 'audit' in t:
                            sys_id = 'security_service'
                        elif 'identity' in t or 'tombstone' in t:
                            sys_id = 'identity_service'
                        
                        parsed_records.append({
                            'evidence_id': fid,
                            'captured_at': cap,
                            'system_id': sys_id,
                            'resource_id': res_id,
                            'data_category': t,
                            'raw_status': rd.get('account_status') or rd.get('status'),
                            'identifier': email or user_ref,
                            'user_id': u,
                            'origin': origin,
                            'details': rd
                        })
            finally:
                conn.close()
        except Exception as e:
            pass

    # 4. LOG files
    elif ext == '.log':
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if not line.strip():
                    continue
                pairs = {}
                for m in KV_PATTERN.finditer(line):
                    k = m.group(1)
                    v = m.group(2) if m.group(2) is not None else m.group(3)
                    pairs[k] = v
                if 'resource_id' in pairs:
                    res_id = pairs.get('resource_id')
                    email = pairs.get('email') or (pairs.get('lookup_key') if pairs.get('lookup_key') and '@' in pairs['lookup_key'] else None)
                    user_ref = pairs.get('customer_reference') or pairs.get('subject_reference') or (pairs.get('lookup_key') if pairs.get('lookup_key') and pairs['lookup_key'].startswith('user_') else None)
                    u = resolve_user(email=email, user_id=user_ref)
                    sys_id = pairs.get('service') or pairs.get('source')
                    parsed_records.append({
                        'evidence_id': fid,
                        'captured_at': cap,
                        'system_id': sys_id,
                        'resource_id': res_id,
                        'data_category': pairs.get('event'),
                        'raw_status': pairs.get('result') or pairs.get('http_status'),
                        'identifier': email or user_ref,
                        'user_id': u,
                        'origin': origin,
                        'details': pairs
                    })

df_parsed = pd.DataFrame(parsed_records)
print(f"Total parsed evidence records: {len(df_parsed)}")
print(f"Unique resource_ids: {df_parsed['resource_id'].nunique()}")
print(f"Records with resolved user_id: {df_parsed['user_id'].notna().sum()}")
print("Sample parsed records:")
print(df_parsed[['evidence_id', 'system_id', 'resource_id', 'user_id', 'identifier', 'raw_status']].head(10))
