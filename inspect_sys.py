import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')
df_sys = pd.read_csv('dataset/system_activity.csv')
for i in range(3681, 3695):
    r = df_sys.iloc[i]
    print(f"{r['activity_id']} | {r['event_time']} | {r['event_type']} | {r['source_system']}->{r['target_system']} | res={r['resource_id']} | {r['reported_result']} | {r['details']}")
