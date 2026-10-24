import re, sys

sys.stdout.reconfigure(encoding='utf-8')

KV_PATTERN = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|([^\s]+))')

with open('dataset/evidence/logs/service_events_ap_south_20260915.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()

traces = {}
for line in lines:
    pairs = {}
    for m in KV_PATTERN.finditer(line):
        k = m.group(1)
        v = m.group(2) if m.group(2) is not None else m.group(3)
        pairs[k] = v
    tr = pairs.get('trace_id')
    if tr:
        traces.setdefault(tr, []).append(pairs)

print(f"Total traces in evidence_01: {len(traces)}")

# Check for emails of cases 12, 15, 17, 19
target_emails = ['minjun.kim@gmail.com', 'lucia-torres@gmail.com', 'leonie.g9352@outlook.com', 'e.varga90@yahoo.com']

for tr, pairs_list in traces.items():
    combined = {}
    for p in pairs_list:
        combined.update(p)
    match_key = combined.get('match_key') or combined.get('lookup_key') or combined.get('email') or combined.get('customer_email')
    for temail in target_emails:
        if match_key and temail in match_key:
            print(f"Matched {temail} in trace {tr}:")
            print(f"  Service: {combined.get('service')}, res_id: {combined.get('resource_id')}, event: {combined.get('event')}, result: {combined.get('result')}")
