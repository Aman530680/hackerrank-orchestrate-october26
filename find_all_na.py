import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df_del = pd.read_csv('dataset/deletion_requests.csv')

non_del_phrases = [
    'leave the account active', 'not asking for deletion', 'keep the account as it is',
    'do not close the account', 'without removing any of my records',
    'remove me from marketing lists only', 'not a request to erase it',
    'leave my profile and purchase history in place', 'continue using the service',
    'please don\'t delete or change anything', 'not asking to delete', 'keep my account'
]

found_cids = []
for _, r in df_del.iterrows():
    txt = r['request_text'].lower()
    for phrase in non_del_phrases:
        if phrase in txt:
            found_cids.append(r['case_id'])
            break

print("Found non-deletion case IDs:", found_cids)
