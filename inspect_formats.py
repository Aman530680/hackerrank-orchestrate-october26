import json, os, sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. records_assurance_snapshot_bundle (e.g. evidence_02)
with open('dataset/evidence/records/customer_data_snapshot_bundle_20260917.json') as f:
    d = json.load(f)
print("=== records_assurance_snapshot_bundle (evidence_02) ===")
print("Keys:", d.keys())
print("Snapshots count:", len(d.get('snapshots', [])))
for s in d.get('snapshots', [])[:3]:
    print("  Snapshot:", s.get('data_store'), s.get('collection'), "records:", len(s.get('records', [])))
    if s.get('records'):
        print("    Sample record:", s.get('records')[0])

# 2. customer_data_inventory_capture (e.g. evidence_93)
with open('dataset/evidence/databases/customer_data_inventory_20260916.sql') as f:
    sql = f.read()
print("\n=== customer_data_inventory_capture (evidence_93) ===")
print(sql[:800])

# 3. service_readback_logs (e.g. evidence_94)
with open('dataset/evidence/logs/resource_lookup_trace_20260926_103856.log') as f:
    log = f.read()
print("\n=== service_readback_logs (evidence_94) ===")
print('\n'.join(log.splitlines()[:10]))

# 4. central_observability_export (e.g. evidence_01)
with open('dataset/evidence/logs/service_events_ap_south_20260915.log') as f:
    log = f.read()
print("\n=== central_observability_export (evidence_01) ===")
print('\n'.join(log.splitlines()[:10]))
