import pandas as pd

df_del = pd.read_csv('dataset/deletion_requests.csv')
print(f"Total requests: {len(df_del)}")

# Let's inspect some request_text samples
for i, r in df_del.head(20).iterrows():
    print(f"[{r['case_id']}] {r['request_text'][:120]}")
