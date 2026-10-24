import json, os, sys, re, sqlite3

sys.stdout.reconfigure(encoding='utf-8')

KV_PATTERN = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))')

def parse_log_file(log_text, file_id, captured_at):
    records = []
    for line in log_text.splitlines():
        line = line.strip()
        if not line:
            continue
        pairs = dict()
        for m in KV_PATTERN.finditer(line):
            k = m.group(1)
            v = m.group(2) if m.group(2) is not None else m.group(3)
            pairs[k] = v
        if 'resource_id' in pairs or 'lookup_key' in pairs or 'event' in pairs:
            res_id = pairs.get('resource_id')
            email = pairs.get('email')
            if not email and pairs.get('lookup_key') and '@' in pairs['lookup_key']:
                email = pairs['lookup_key']
            user_ref = pairs.get('customer_reference') or pairs.get('subject_reference')
            if not user_ref and pairs.get('lookup_key') and pairs['lookup_key'].startswith('user_'):
                user_ref = pairs['lookup_key']
            
            records.append({
                'file_id': file_id,
                'captured_at': captured_at,
                'system_id': pairs.get('service'),
                'resource_id': res_id,
                'email': email,
                'user_id': user_ref,
                'event': pairs.get('event'),
                'pairs': pairs
            })
    return records

# Test on evidence_94
with open('dataset/evidence/logs/resource_lookup_trace_20260926_103856.log', 'r', encoding='utf-8') as f:
    e94_recs = parse_log_file(f.read(), 'evidence_94', '2026-09-26T10:38:56Z')
print(f"evidence_94 parsed {len(e94_recs)} records. Sample with resource_id:")
with_res = [r for r in e94_recs if r['resource_id']]
print(f"  Total with resource_id: {len(with_res)}")
for r in with_res[:3]:
    print(" ", r)
