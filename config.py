"""Configuration from environment. No frameworks."""
import os

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o")
OPENAI_MAX_TOKENS = int(os.environ.get("OPENAI_MAX_TOKENS", "16384"))
MAX_FILE_SIZE_BYTES = int(os.environ.get("MAX_FILE_SIZE_BYTES", "100000"))
MAX_TOTAL_CHARS = int(os.environ.get("MAX_TOTAL_CHARS", "300000"))
