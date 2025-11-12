# config.py
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:1235/v1")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY",  "sk-no-key-needed")
OPENAI_MODEL    = os.getenv("OPENAI_MODEL",    "local-model")  # llama_cpp.server default

DB_PATH = os.getenv("DB_PATH", str(PROJECT_ROOT / "data" / "mock_parts.db"))
SQL_DIR = PROJECT_ROOT / "sql"
