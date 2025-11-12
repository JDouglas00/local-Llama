# batch/run_batch.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from client import client
from config import MODEL
from pathlib import Path

def ask(q: str):
    r = client.chat.completions.create(
        model=MODEL,
        messages=[{"role":"user","content":q}],
        temperature=0.2,
        max_tokens=120,
        seed=7
    )
    return r.choices[0].message.content.strip()

if __name__ == "__main__":
    prompts = [p.strip() for p in Path(__file__).with_name("prompts.txt").read_text(encoding="utf-8").splitlines() if p.strip()]

    results = []
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = {ex.submit(ask, q): q for q in prompts}
        for fut in as_completed(futs):
            q = futs[fut]
            try:
                a = fut.result()
            except Exception as e:
                a = f"[ERROR] {e}"
            results.append((q, a))

    # Save a simple TSV
    out = Path(__file__).with_name("batch_output.tsv")
    out.write_text("\n".join(f"{q}\t{a}" for q, a in results), encoding="utf-8")
    print(f"Wrote {out} with {len(results)} rows.")
