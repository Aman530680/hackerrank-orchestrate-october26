import pandas as pd

df_del = pd.read_csv('dataset/deletion_requests.csv')
print("Unique audit_at values in deletion_requests.csv:", df_del['audit_at'].nunique())
print(df_del['audit_at'].value_counts())
