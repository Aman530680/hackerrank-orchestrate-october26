import json, os, sys, re, sqlite3
import pandas as pd
from pypdf import PdfReader

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
                        'origin': origin,
                        'raw_record': {'line': line}
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
                            if not email and item.get('query') and '@' in item['query']:
                                email = item['query']
                            user_ref = item.get('customer_reference') or item.get('subject_reference')
                            u = resolve_user(email=email, user_id=user_ref)
                            
                            # Check status
                            st = item.get('status_code') or item.get('last_delivery_status') or item.get('event_code')
                            if item.get('enabled') is True:
                                st = 'ACTIVE'
                            elif item.get('enabled') is False:
                                st = 'DISABLED'
                            if item.get('restore_allowed') is True:
                                st = 'ACTIVE'
                            elif item.get('restore_allowed') is False:
                                st = 'BLOCKED'
                            if item.get('hits') and isinstance(item['hits'], dict):
                                hits = item['hits']
                                if hits.get('total', 0) > 0:
                                    st = 'FOUND'
                                    for doc in hits.get('documents', []):
                                        if not email:
                                            email = doc.get('email')
                                        if not user_ref:
                                            user_ref = doc.get('customer_reference')
                                    u = resolve_user(email=email, user_id=user_ref)
                                else:
                                    st = 'NOT_FOUND'
                                    
                            parsed_records.append({
                                'evidence_id': fid,
                                'captured_at': cap,
                                'system_id': sys_id,
                                'resource_id': res_id,
                                'data_category': coll_name,
                                'raw_status': st,
                                'identifier': email or user_ref,
                                'user_id': u,
                                'origin': origin,
                                'raw_record': item
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
                            'raw_status': item.get('account_status') or item.get('status'),
                            'identifier': email or user_ref,
                            'user_id': u,
                            'origin': origin,
                            'raw_record': item
                        })
                        
            # Type C: export_manifest or jobs
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
                        'raw_record': item
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
                        'raw_record': item
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
                        
                        # Handle inner record_json if present
                        inner_dict = {}
                        if 'record_json' in rd and rd['record_json']:
                            try:
                                inner_dict = json.loads(rd['record_json'])
                            except:
                                pass
                        
                        email = rd.get('email') or inner_dict.get('email')
                        if not email and isinstance(inner_dict.get('document'), dict):
                            email = inner_dict['document'].get('email')
                        user_ref = rd.get('customer_reference') or rd.get('user_id') or inner_dict.get('user_id') or inner_dict.get('customer_reference') or inner_dict.get('subject_reference')
                        u = resolve_user(email=email, user_id=user_ref)
                        
                        sys_id = 'account_service'
                        orig_sys = rd.get('origin_system') or inner_dict.get('origin_system')
                        if orig_sys:
                            sys_id = orig_sys
                        elif 'search' in t:
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
                            'raw_status': rd.get('account_status') or rd.get('status') or inner_dict.get('account_status'),
                            'identifier': email or user_ref,
                            'user_id': u,
                            'origin': origin,
                            'raw_record': rd
                        })
            finally:
                conn.close()
        except Exception as e:
            pass

    # 4. LOG files
    elif ext == '.log':
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # Group by trace_id when available
        trace_map = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            pairs = {}
            for m in KV_PATTERN.finditer(line):
                k = m.group(1)
                v = m.group(2) if m.group(2) is not None else m.group(3)
                pairs[k] = v
            tr = pairs.get('trace_id')
            if tr:
                trace_map.setdefault(tr, []).append(pairs)
            else:
                # Standalone log event
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
                        'raw_record': pairs
                    })
        
        for tr, pairs_list in trace_map.items():
            combined = {}
            for p in pairs_list:
                combined.update(p)
            res_id = combined.get('resource_id')
            email = combined.get('email') or combined.get('match_key') or combined.get('lookup_key') or combined.get('subject_key') or combined.get('customer_email')
            if email and '@' not in email:
                email = None
            user_ref = combined.get('customer_reference') or combined.get('subject_reference') or combined.get('correlation_key')
            if not user_ref and combined.get('lookup_key') and combined['lookup_key'].startswith('user_'):
                user_ref = combined['lookup_key']
            u = resolve_user(email=email, user_id=user_ref)
            sys_id = combined.get('service')
            parsed_records.append({
                'evidence_id': fid,
                'captured_at': cap,
                'system_id': sys_id,
                'resource_id': res_id,
                'data_category': combined.get('event'),
                'raw_status': combined.get('http_status') or combined.get('result') or combined.get('eligible'),
                'identifier': email or user_ref,
                'user_id': u,
                'origin': origin,
                'raw_record': combined
            })

    # 5. PDF files
    elif ext == '.pdf':
        try:
            reader = PdfReader(fpath)
            txt = ""
            for page in reader.pages:
                txt += page.extract_text() or ""
            
            # Look for resource_id pattern
            res_matches = re.findall(r'\b(?:account|analytics|support|search|data_flow|backup|audit_record|export|tombstone)_[0-9]+\b', txt)
            # Find emails
            email_matches = [e for e in email_to_user.keys() if e in txt.lower()]
            # Find user_ids
            user_matches = [u for u in user_to_emails.keys() if u in txt]
            
            for res_id in set(res_matches):
                u = user_matches[0] if user_matches else (email_to_user[email_matches[0]] if email_matches else None)
                parsed_records.append({
                    'evidence_id': fid,
                    'captured_at': cap,
                    'system_id': 'support_platform' if 'support' in res_id else ('security_service' if 'audit' in res_id else 'export_service'),
                    'resource_id': res_id,
                    'data_category': 'DOCUMENT_ATTACHMENT',
                    'raw_status': 'FOUND',
                    'identifier': email_matches[0] if email_matches else (user_matches[0] if user_matches else None),
                    'user_id': u,
                    'origin': origin,
                    'raw_record': {'text': txt[:500]}
                })
        except Exception as e:
            pass

df_all_ev = pd.DataFrame(parsed_records)
print(f"Total parsed records: {len(df_all_ev)}")
print(f"Unique resources: {df_all_ev['resource_id'].nunique()}")
print(f"Records with resolved user_id: {df_all_ev['user_id'].notna().sum()}")
df_all_ev.to_pickle('dataset/parsed_evidence.pkl')
print("Saved parsed evidence to dataset/parsed_evidence.pkl")
