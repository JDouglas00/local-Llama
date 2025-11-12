# rag/answer.py
import os, sys, textwrap, requests
from utils import embed_text, load_index, simple_score

LLAMA_BASE  = os.environ.get("LLAMA_BASE", "http://127.0.0.1:1235")
CHAT_URL    = f"{LLAMA_BASE}/v1/chat/completions"
MODEL_NAME  = os.environ.get("LLAMA_MODEL", "local-model")
INDEX_DIR   = os.path.join(os.path.dirname(__file__), "index")

TOP_K       = int(os.environ.get("RAG_TOP_K", "6"))    # top chunks (not files)
MAX_FILES   = int(os.environ.get("RAG_MAX_FILES", "3"))
QUOTE_LINES = int(os.environ.get("RAG_QUOTE_LINES", "10"))

SYSTEM = """You are a concise factory assistant. Answer ONLY from the provided CONTEXT. If it is not in CONTEXT, say you don't have enough information. Put safety steps first if relevant."""

USER_TMPL = """QUESTION:
{question}

CONTEXT (relevant excerpts with file and line numbers):
{context}

Instructions:
- Use ONLY the context above.
- If missing info, say so.
- End with "Sources:" followed by the file paths you used.
"""

def fetch_completion(messages, temperature=0.2, max_tokens=400):
    headers = {"Authorization": "Bearer sk-no-key-needed"}
    payload = {"model": MODEL_NAME, "messages": messages,
               "temperature": temperature, "max_tokens": max_tokens}
    r = requests.post(CHAT_URL, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def dedupe_preserve_order(items):
    seen, out = set(), []
    for it in items:
        if it not in seen:
            out.append(it); seen.add(it)
    return out

def build_context(question, idxs, meta):
    # Group top chunks by file; rerank within file by simple term score
    from collections import defaultdict

    by_file = defaultdict(list)
    for i in idxs:
        m = meta[i]
        by_file[m["path"]].append(m)

    # keep only top MAX_FILES files by the best chunk score
    scored_files = []
    for path, entries in by_file.items():
        best = max(entries, key=lambda e: simple_score(question, f"{path}:{e['start']}-{e['end']}"))
        scored_files.append((path, best))
    scored_files.sort(key=lambda x: simple_score(question, f"{x[0]}:{x[1]['start']}-{x[1]['end']}"), reverse=True)
    picked_files = [p for p,_ in scored_files[:MAX_FILES]]

    # For each chosen file, open and quote the chosen spans
    blocks = []
    used_files = []
    for fpath in picked_files:
        try:
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
        except Exception as e:
            lines = [f"[cannot read {fpath}: {e}]"]

        # Choose up to 2 top chunks from this file
        chunks = [m for m in meta if m["path"] == fpath]
        # rerank by proximity to question (cheap)
        chunks.sort(key=lambda m: simple_score(question, f"{fpath}:{m['start']}-{m['end']}"), reverse=True)
        chosen = chunks[:2]

        for c in chosen:
            s = max(0, c["start"])
            e = min(len(lines), c["end"])
            window = "\n".join(f"{i+1:>4}: {lines[i]}" for i in range(s, min(e, s+QUOTE_LINES)))
            blocks.append(f"---\nFILE: {fpath}\nLINES: {s+1}-{min(e, s+QUOTE_LINES)}\n{window}\n")
            used_files.append(fpath)

    used_files = dedupe_preserve_order(used_files)
    return "\n".join(blocks), used_files

def main():
    if len(sys.argv) < 2:
        print('Usage: .\\.venv\\Scripts\\python .\\rag\\answer.py "your question"')
        sys.exit(1)

    question = sys.argv[1]
    M, meta = load_index(INDEX_DIR)
    qvec = embed_text(question, dim=M.shape[1])

    # cosine sim inlined (avoid importing more helpers)
    import numpy as np
    sims = (M @ qvec) / (np.linalg.norm(M, axis=1) * np.linalg.norm(qvec) + 1e-9)
    idxs = list(np.argsort(-sims)[:TOP_K])

    ctx, sources = build_context(question, idxs, meta)

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER_TMPL.format(question=question, context=ctx)}
    ]
    try:
        out = fetch_completion(messages)
    except Exception as e:
        print(f"[error] Llama call failed: {e}")
        print("Is the server running at:", CHAT_URL)
        sys.exit(2)

    print("\n=== Answer ===\n")
    print(textwrap.dedent(out).strip())
    print("\n=== Sources ===")
    for s in sources:
        print(s)

if __name__ == "__main__":
    main()

