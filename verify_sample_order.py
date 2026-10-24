import pandas as pd
import json, sys

sys.stdout.reconfigure(encoding='utf-8')

df_out = pd.read_csv('dataset/sample_output.csv')

OP_ORDER = {
    # Phase FINDING
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    # Phase REMEDIATION
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    # Phase VERIFICATION
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}

PHASE_ORDER = {
    'FINDING': 1,
    'REMEDIATION': 2,
    'VERIFICATION': 3
}

all_ordered = True
for _, row in df_out.iterrows():
    cid = row['case_id']
    steps = json.loads(row['steps_json'])
    
    # Check if steps are sorted by:
    # (PHASE_ORDER[phase], OP_ORDER[operation], system_id, resource_id)
    keys = []
    for s in steps:
        p_idx = PHASE_ORDER[s['phase']]
        o_idx = OP_ORDER[s['operation']]
        keys.append((p_idx, o_idx, s['system_id'], s['resource_id']))
        
    sorted_keys = sorted(keys)
    if keys != sorted_keys:
        all_ordered = False
        print(f"[{cid}] Order mismatch!")
        print("  Actual:", keys)
        print("  Sorted:", sorted_keys)

if all_ordered:
    print("ALL 32 SAMPLE CASES IN SAMPLE_OUTPUT.CSV FOLLOW THIS EXACT SORTING KEY PERFECTLY!")
