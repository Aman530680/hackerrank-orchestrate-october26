import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df_del = pd.read_csv('dataset/deletion_requests.csv')
print("Unique request text templates count:", df_del['request_text'].nunique())

# Let's check non-English texts
import re
non_ascii = df_del[df_del['request_text'].str.contains(r'[^\x00-\x7F]')]
print("Non-ascii requests count:", len(non_ascii))
for cid, txt in zip(non_ascii['case_id'], non_ascii['request_text']):
    # check first 40 chars
    first_few = txt[:60]
    print(f"[{cid}] {first_few}")
