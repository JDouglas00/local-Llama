# rag/query.py
import sys, os
import numpy as np
from utils import embed_text, load_index, top_k_cosine

INDEX_DIR = os.path.join(os.path.dirname(__file__), "index")

def main():
    if len(sys.argv) < 2:
        print("Usage: python rag/query.py \"your question here\"")
        sys.exit(1)

    question = sys.argv[1]
    mat, meta = load_index(INDEX_DIR)
    qvec = embed_text(question, dim=mat.shape[1])
    idxs = top_k_cosine(qvec, mat, k=5)

    print("\nTop matches:")
    for rank, i in enumerate(idxs, start=1):
        p = meta[i]["path"]
        print(f"{rank}. {p}")

    # show a snippet of the best match
    best_path = meta[idxs[0]]["path"]
    print("\nBest match snippet:")
    try:
        with open(best_path, "r", encoding="utf-8", errors="ignore") as f:
            txt = f.read()
        print(txt[:500])
    except Exception as e:
        print(f"[warn] could not open {best_path}: {e}")

if __name__ == "__main__":
    main()

