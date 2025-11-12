# rag/build_index.py
import os, json, numpy as np
from utils import read_txt, split_into_lines, chunk_by_lines, embed_text, save_index

ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(ROOT, "data", "sop")
INDEX_DIR = os.path.join(ROOT, "index")

DIM = 1024              # keep in sync with query/answer
CHUNK_SIZE = 12         # lines per chunk
OVERLAP = 3

def main():
    rows = []
    meta = []
    for root, _, files in os.walk(DATA_DIR):
        for name in files:
            if not name.lower().endswith(".txt"): 
                continue
            path = os.path.join(root, name)
            text = read_txt(path)
            lines = split_into_lines(text)
            chunks = chunk_by_lines(lines, CHUNK_SIZE, OVERLAP)
            for c in chunks:
                vec = embed_text(c["text"], dim=DIM)
                rows.append(vec)
                meta.append({"path": path, "start": c["start"], "end": c["end"]})
    if not rows:
        print("[warn] no .txt files found")
        return
    M = np.vstack(rows).astype("float32")
    save_index(INDEX_DIR, M, meta)
    print(f"[ok] built index: {len(rows)} chunks, dim={DIM}")
    print(f"[ok] saved to: {os.path.join(INDEX_DIR, 'matrix.npy')} and meta.json")

if __name__ == "__main__":
    main()
