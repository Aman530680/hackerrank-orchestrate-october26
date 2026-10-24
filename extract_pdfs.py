import zlib, re, os, sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_dir = 'dataset/evidence/documents'
for f in os.listdir(pdf_dir):
    if f.endswith('.pdf'):
        p = os.path.join(pdf_dir, f)
        with open(p, 'rb') as fp:
            data = fp.read()
        print(f"\n=== {f} ({len(data)} bytes) ===")
        # Find stream objects
        idx = 0
        while True:
            start = data.find(b'stream', idx)
            if start == -1:
                break
            # move past stream\r\n or stream\n
            if data[start:start+7] == b'stream\n':
                s_start = start + 7
            elif data[start:start+8] == b'stream\r\n':
                s_start = start + 8
            else:
                s_start = start + 6
            end = data.find(b'endstream', s_start)
            if end == -1:
                break
            s_bytes = data[s_start:end].strip()
            idx = end + 9
            try:
                dec = zlib.decompress(s_bytes)
                # print any text strings
                # In PDF, text is often in (text) Tj or TJ
                strings = re.findall(rb'\((.*?)\)', dec)
                txt = " ".join([s.decode('latin1', errors='ignore') for s in strings if len(s) > 1])
                if txt:
                    print("  Text:", txt[:300])
            except Exception as e:
                pass
