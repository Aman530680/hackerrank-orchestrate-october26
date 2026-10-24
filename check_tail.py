import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df_del = pd.read_csv('dataset/deletion_requests.csv')

# Let's inspect cases 520 to 550
print("Cases 525 to 550:")
for _, r in df_del.tail(30).iterrows():
    print(f"[{r['case_id']}] reported={r['reported_status']} | text={r['request_text']}")
