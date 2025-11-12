# rag/utils.py (append or merge carefully)
import os, json, re, math, numpy as np

def read_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def split_into_lines(text):
    return text.splitlines()

def chunk_by_lines(lines, chunk_size=12, overlap=3):
    chunks = []
    i = 0
    while i < len(lines):
        start = i
        end = min(len(lines), i + chunk_size)
        chunk_lines = lines[start:end]
        chunks.append({
            "start": start, "end": end,
            "text": "\n".join(chunk_lines)
        })
        if end == len(lines): break
        i = end - overlap
    return chunks

def simple_score(query, text):
    """Very light term frequency score for reranking chunks."""
    q_terms = re.findall(r"\w+", query.lower())
    t = text.lower()
    return sum(t.count(qt) for qt in q_terms)

def load_index(index_dir):
    mat = np.load(os.path.join(index_dir, "matrix.npy"))
    with open(os.path.join(index_dir, "meta.json"), "r", encoding="utf-8") as f:
        meta = json.load(f)
    return mat, meta

def save_index(index_dir, mat, meta):
    os.makedirs(index_dir, exist_ok=True)
    np.save(os.path.join(index_dir, "matrix.npy"), mat)
    with open(os.path.join(index_dir, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

def embed_text(text, dim=1024, seed=0):
    rng = np.random.default_rng(
        abs(hash(text)) % (2**32) if seed == 0 else seed
    )
    v = rng.normal(size=dim).astype(np.float32)
    v /= np.linalg.norm(v) + 1e-9
    return v

def top_k_cosine(q, M, k=3):
    sims = (M @ q) / (np.linalg.norm(M, axis=1) * np.linalg.norm(q) + 1e-9)
    return list(np.argsort(-sims)[:k])
