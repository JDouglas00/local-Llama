# client.py
import requests
from typing import List, Dict, Any
from config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL

HEADERS = {"Authorization": f"Bearer {OPENAI_API_KEY}"}

def chat(messages: List[Dict[str, str]], stream: bool=False, **kwargs) -> str:
    payload = {"model": OPENAI_MODEL, "messages": messages, **kwargs}
    url = f"{OPENAI_BASE_URL}/chat/completions"
    r = requests.post(url, headers=HEADERS, json=payload, stream=stream, timeout=300)

    if not stream:
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

    # simple streaming printer
    r.raise_for_status()
    text = []
    for line in r.iter_lines():
        if not line or not line.startswith(b"data:"):
            continue
        chunk = line[len(b"data:"):].strip()
        if chunk == b"[DONE]":
            break
        delta = r.json() if False else None  # guarded; we parse below
        try:
            piece = (requests.utils.json.loads(chunk)
                     ["choices"][0]["delta"].get("content", ""))
            print(piece, end="", flush=True)
            text.append(piece)
        except Exception:
            pass
    print()
    return "".join(text)
 