import pandas as pd
import json

df_req = pd.read_csv('dataset/sample_deletion_requests.csv')
df_out = pd.read_csv('dataset/sample_output.csv')

merged = pd.merge(df_req, df_out, on='case_id')
print(pd.crosstab(merged['reported_status'], merged['deletion_status']))
