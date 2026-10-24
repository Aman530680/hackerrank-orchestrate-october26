import pandas as pd
import re, sys

sys.stdout.reconfigure(encoding='utf-8')
df_sys = pd.read_csv('dataset/system_activity.csv')

# Let's search for user_ in details
user_matches = df_sys[df_sys['details'].str.contains(r'user_', regex=True, na=False)]
print(f"Events with 'user_' in details: {len(user_matches)}")
print(user_matches.head(10)[['activity_id', 'event_type', 'resource_id', 'details']])

# Let's search for @ in details (emails)
email_matches = df_sys[df_sys['details'].str.contains(r'@', regex=True, na=False)]
print(f"\nEvents with email '@' in details: {len(email_matches)}")
print(email_matches.head(10)[['activity_id', 'event_type', 'resource_id', 'details']])
