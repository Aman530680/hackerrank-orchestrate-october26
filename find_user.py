import os
import re

targets = ['Amina', 'Elmasri', 'amina.elmasri', '812 7394', '2b97c4']
for root, dirs, files in os.walk('dataset'):
    for file in files:
        if file.endswith(('.csv', '.json', '.txt', '.log', '.sql')):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    for t in targets:
                        if t in content:
                            print(f"Target '{t}' found in: {path}")
            except Exception as e:
                pass
