import os, sys, json, requests, textwrap
from utils import embed_text, load_index

LLAMA_BASE = os.environ.get("LLAMA_BASE", "http://127.0.0.1:1235")
CHAT_URL   = f"{LLAMA_BASE}/v1/chat/completions"
MODEL_NAME = os.environ.get("LLAMA_MODEL", "local-model")
INDEX_DIR  = os.path.join(os.path.dirname(__file__), "index")

SCHEMA_HINT = """
Return ONLY JSON (no markdown). Schema:
{
  "answer": "string — concise final answer grounded in context or 'insufficient context'",
  "bullets": ["string", "..."], 
  "safety_steps": ["string", "..."], 
  "sources": ["absolute file paths"]
}
"""

def ask(messages):
    headers = {"Authorization":"Bearer sk-no-key-needed"}
    payload = {"model": MODEL_NAME, "messages": messages, "temperature": 0.1, "max_tokens": 500}
    r = requests.post(CHAT_URL, json=payload, headers=headers, timeout=120)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def main():
    if len(sys.argv) < 2:
        print('Usage: .\\.venv\\Scripts\\python .\\rag\\answer_json.py "question"')
        sys.exit(1)

    q = sys.argv[1]
    M, meta = load_index(INDEX_DIR)
    qvec = embed_text(q, dim=M.shape[1])

    import numpy as np
    sims = (M @ qvec) / (np.linalg.norm(M, axis=1) * np.linalg.norm(qvec) + 1e-9)
    idxs = list(np.argsort(-sims)[:5])

    # gather small raw snippets to keep prompt tight
    context = []
    used = []
    for i in idxs:
        m = meta[i]
        path = m["path"]
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
        except:
            lines = []
        s, e = m["start"], min(m["end"], m["start"]+8)
        snippet = "\n".join(lines[s:e])
        context.append(f"FILE: {path}\nLINES: {s+1}-{e}\n{snippet}")
        used.append(path)

    messages = [
        {"role":"system","content":"You are precise and only use the provided CONTEXT."},
        {"role":"user","content": f"QUESTION:\n{q}\n\nCONTEXT:\n" + "\n---\n".join(context) + "\n\n" + SCHEMA_HINT}
    ]
    raw = ask(messages)

    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        doc = {"answer": raw.strip(), "bullets": [], "safety_steps": [], "sources": list(dict.fromkeys(used))}
    # print nicely
    print("\nAnswer:", doc.get("answer","").strip())
    if doc.get("safety_steps"):
        print("\nSafety steps:")
        for s in doc["safety_steps"]: print("-", s)
    if doc.get("bullets"):
        print("\nDetails:")
        for b in doc["bullets"]: print("-", b)
    if doc.get("sources"):
        print("\nSources:")
        for s in doc["sources"]: print(s)

if __name__ == "__main__":
    main()
