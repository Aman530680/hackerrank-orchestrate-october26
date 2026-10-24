import os, sys, json, re, sqlite3
import pandas as pd
from pypdf import PdfReader

# Helper for phase and op ordering
OP_ORDER = {
    'REPORT_REMAINING_RECORD': 1,
    'REPORT_EXPOSED_PII': 2,
    'REPORT_ACTIVE_DATA_FLOW': 3,
    'REPORT_RESTORE_RISK': 4,
    'DISABLE_DATA_FLOW': 1,
    'BLOCK_RESTORE': 2,
    'DELETE_RECORD': 3,
    'REDACT_RECORD': 4,
    'ANONYMIZE_RECORD': 5,
    'VERIFY_RECORD_ABSENT': 1,
    'VERIFY_RECORD_PRESENT': 2,
    'VERIFY_RECORD_REDACTED': 3,
    'VERIFY_RECORD_ANONYMIZED': 4,
    'VERIFY_DATA_FLOW_DISABLED': 5,
    'VERIFY_RESTORE_BLOCKED': 6,
}
PHASE_ORDER = {'FINDING': 1, 'REMEDIATION': 2, 'VERIFICATION': 3}

NON_DEL_PHRASES = [
    'leave the account active', 'not asking for deletion', 'keep the account as it is',
    'do not close the account', 'without removing any of my records',
    'remove me from marketing lists only', 'not a request to erase it',
    'leave my profile and purchase history in place', 'continue using the service',
    'please don\'t delete or change anything', 'not asking to delete', 'keep my account'
]

def is_deletion_request(text):
    if not text or pd.isna(text):
        return True
    t = str(text).lower()
    for phrase in NON_DEL_PHRASES:
        if phrase in t:
            return False
    return True

def sort_and_renumber(steps):
    def sort_key(s):
        return (PHASE_ORDER[s['phase']], OP_ORDER[s['operation']], s['system_id'], s['resource_id'])
    sorted_steps = sorted(steps, key=sort_key)
    for idx, s in enumerate(sorted_steps, 1):
        s['step_no'] = idx
    return sorted_steps

print("Helper functions ready.")
