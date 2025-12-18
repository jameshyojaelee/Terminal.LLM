import os
import sys

if sys.version_info < (3, 10):
    raise SystemExit(
        f"Python 3.10+ required. You're running {sys.version.split()[0]} from:\n"
        f"  {sys.executable}\n"
        "If you're in a virtualenv, you likely created it with an older Python.\n"
        "Recreate it with a newer interpreter, e.g.\n"
        "  rm -rf .venv\n"
        "  python3.12 -m venv .venv\n"
        "  source .venv/bin/activate\n"
        "Then re-run this script."
    )

try:
    import google.generativeai as genai
except ModuleNotFoundError:
    raise SystemExit(
        "Missing dependency: google-generativeai\n"
        "Install it with:\n"
        f"  {sys.executable} -m pip install google-generativeai"
    )

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise SystemExit(
        "Missing GOOGLE_API_KEY. Set it and re-run, e.g.\n"
        "  export GOOGLE_API_KEY='YOUR_KEY_HERE'\n"
        f"  {sys.executable} check_models.py"
    )

genai.configure(api_key=API_KEY)

print("--- AVAILABLE MODELS ---")
try:
    for m in genai.list_models():
        # We only care about models that can generate text (generateContent)
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
