import pandas as pd
import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')
df_sys = pd.read_csv('dataset/system_activity.csv')
df_ev = pd.read_csv('dataset/evidence_files.csv')

# Load all evidence text/content into memory
ev_contents = {}
for _, r in df_ev.iterrows():
    fid = r['file_id']
    fpath = os.path.join('dataset', r['file_path'])
    if os.path.exists(fpath):
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            ev_contents[fid] = f.read()

# For each sample step, check where resource_id appears
all_steps = []
for _, r in df_out.iterrows():
    cid = r['case_id']
    steps = json.loads(r['steps_json'])
    for s in steps:
        all_steps.append((cid, s))

print(f"Total steps across 32 sample cases: {len(all_steps)}")

missing_in_sys = []
missing_in_ev = []

for cid, s in all_steps:
    res = s['resource_id']
    sys_count = len(df_sys[df_sys['resource_id'] == res])
    
    # check in evidence files
    ev_matches = [fid for fid, content in ev_contents.items() if res in content]
    
    if sys_count == 0:
        missing_in_sys.append((cid, s, ev_matches))
    if len(ev_matches) == 0:
        missing_in_ev.append((cid, s, sys_count))

print(f"Resources missing from system_activity: {len(missing_in_sys)}")
for cid, s, evm in missing_in_sys[:10]:
    print(f"  [{cid}] {s['system_id']} {s['resource_id']} {s['operation']} -> found in ev: {evm}")

print(f"Resources missing from evidence: {len(missing_in_ev)}")
for cid, s, sc in missing_in_ev[:10]:
    print(f"  [{cid}] {s['system_id']} {s['resource_id']} {s['operation']} -> found in sys: {sc}")
