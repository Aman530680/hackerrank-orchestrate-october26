import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

df_del = pd.read_csv('dataset/deletion_requests.csv')

deletion_keywords = [
    'delet', 'eras', 'close', 'clos', 'remov', 'supprim', 'elimin', 'eliminar', 
    'cancell', 'lösch', 'borr', 'tombstone', 'vergess', 'oubli', 'cancella', 
    'suppression', '削除', '消去', 'exclusão', 'exclusao', 'excluir', 'eliminação', 
    'elimina', 'schließen', 'fermer', 'chiudi', 'verwijder', 'удалит'
]

non_del = []
for i, r in df_del.iterrows():
    text = str(r['request_text']).lower()
    has_del = any(kw in text for kw in deletion_keywords)
    if not has_del:
        non_del.append((r['case_id'], r['request_text']))

print(f"Non-deletion candidates: {len(non_del)}")
for cid, txt in non_del:
    print(f"[{cid}] {txt}")
