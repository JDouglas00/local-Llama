# rag/eval.py
import os, json, time, subprocess, sys, shutil, platform
from pathlib import Path

QUESTIONS = [
    "Which categories hold the most inventory value in MAIN?",
    "What are the first safety steps for F07?",
    "How do I reset after clearing a conveyor jam?"
]

HERE = Path(__file__).resolve().parent            # ...\llama_local\rag
ROOT = HERE.parent                                # ...\llama_local
ANSWER = HERE / "answer.py"

def find_python():
    # 1) Prefer the current interpreter (works if you run via the venv)
    py = Path(sys.executable)
    if py.exists():
        return str(py)

    # 2) Fallback to project venv (Windows & POSIX)
    if platform.system() == "Windows":
        cand = ROOT / ".venv" / "Scripts" / "python.exe"
    else:
        cand = ROOT / ".venv" / "bin" / "python"
    if cand.exists():
        return str(cand)

    # 3) Fallback to PATH
    return shutil.which("python") or shutil.which("py") or "python"

def main():
    py = find_python()
    results = []
    for q in QUESTIONS:
        t0 = time.time()
        proc = subprocess.run(
            [py, str(ANSWER), q],
            capture_output=True, text=True,
            cwd=str(HERE)   # run inside rag/
        )
        elapsed = time.time() - t0
        results.append({
            "q": q,
            "elapsed_s": round(elapsed, 2),
            "ok": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr
        })
        print("\n---")
        print("Q:", q)
        print("Time:", round(elapsed, 2), "s")
        # Show the first ~40 lines for quick glance
        preview = (proc.stdout or proc.stderr or "").splitlines()[:40]
        for line in preview:
            print(line)

    out_path = HERE / "eval_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n[ok] wrote {out_path}")

if __name__ == "__main__":
    main()

