import os
import tempfile
import subprocess
import re
import keyboard
import pyperclip
import threading
import sys
from openai import OpenAI

# ====================== НАСТРОЙКИ ======================
API_KEY = "api-nvidia-ai"
BASE_URL = "https://integrate.api.nvidia.com/v1"
MODEL = "meta/llama-3.3-70b-instruct"

SYSTEM_PROMPT = (

)

TRIGGER_HOTKEY = 'ctrl+d'
EXIT_HOTKEY = 'ctrl+q'
# ======================================================

is_processing = False


def clean_code_response(text: str) -> str:
    text = re.sub(r'```(?:csharp|c#|cs|cpp|python|json|xml|yaml)?\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```\s*$', '', text, flags=re.MULTILINE)
    text = text.strip()
    return text


def ask_ai(prompt):
    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4096,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Ошибка: {e}]"


def open_in_notepad(text):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_path = f.name
        subprocess.Popen(['notepad.exe', temp_path], shell=False)
    except Exception:
        pass


def ai_processing_thread(text):
    global is_processing

    raw_response = ask_ai(text)
    clean_response = clean_code_response(raw_response)

    try:
        pyperclip.copy(clean_response)
        open_in_notepad(clean_response)
    except:
        pass
    finally:
        is_processing = False


def process_clipboard_content():
    global is_processing
    if is_processing:
        return

    try:
        content = pyperclip.paste().strip()
        if not content:
            return
    except:
        return

    is_processing = True
    threading.Thread(target=ai_processing_thread, args=(content,), daemon=True).start()


def exit_program():
    sys.exit(0)


if __name__ == "__main__":
    if sys.stdout:
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    keyboard.add_hotkey(TRIGGER_HOTKEY, process_clipboard_content)
    keyboard.add_hotkey(EXIT_HOTKEY, exit_program)

    try:
        keyboard.wait()
    except:
        pass