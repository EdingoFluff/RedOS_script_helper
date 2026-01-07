import json
import time
import pyautogui
import requests
import subprocess
import webbrowser
import re
import sys

# --- КОНФИГУРАЦИЯ API ---
API_KEY = ""
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "kwaipilot/kat-coder-pro:free"

# Улучшенный промпт с четкими правилами и примерами
SYSTEM_PROMPT = """
Ты — модуль управления Red OS. Возвращай ТОЛЬКО валидный JSON-список команд БЕЗ текста, markdown или [].

Формат: [{"action": "hotkey", "params": ["ctrl","alt","t"]}, ...]

**Действия:**
- "hotkey": ["ctrl","alt","t"] или ["enter"]
- "type": ["текст для ввода"] (один элемент!)
- "wait": [число секунд]
- "run_shell": ["команда без терминала"]
- "open_url": ["https://example.com"]
- "mouse_click": [x, y]

**Правила Red OS:**
- Терминал: ctrl+alt+t → type → enter
- Пакеты: dnf вместо apt
- Root: su - → enter → type "1" → enter
- Рабочий стол: /home/sergeykos/Desktop
- Минимум 1 команда, максимум 10
- Каждый пункт (1., 2.) — отдельный JSON-список
"""

def get_ai_instruction(user_text: str, max_retries: int = 4) -> list | None:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Задача: {user_text}"},
        ],
        "temperature": 0.1,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** attempt)
                continue
            
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Очистка markdown и пробелов
            content = re.sub(r'```json\s*|```|\`{1,3}', '', content).strip()
            parsed = json.loads(content)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
            else:
                print("[-] AI вернул пустой или неверный JSON")
        except json.JSONDecodeError:
            print("[-] Неверный JSON от AI")
        except Exception as e:
            print(f"[-] Ошибка AI (попытка {attempt+1}): {e}")
            time.sleep(1)
    return None

def trigger_screen_script():
    """Запуск screen.py в фоне без вывода."""
    try:
        subprocess.Popen(["python3", "screen.py"], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[-] screen.py не найден")
    except Exception as e:
        print(f"[-] Ошибка screen.py: {e}")

def execute_command_list(command_list: list):
    print(f"[*] Выполняю {len(command_list)} команд:")
    for i, cmd in enumerate(command_list, 1):
        action = cmd.get("action")
        params = cmd.get("params", [])
        print(f"  Шаг {i}: {action} {params}")
        
        try:
            if action == "hotkey":
                pyautogui.hotkey(*params)
            elif action == "type":
                if params:
                    pyautogui.write(str(params[0]), interval=0.015)
            elif action == "wait":
                wait_time = float(params[0]) if params else 1.0
                time.sleep(wait_time)
            elif action == "run_shell":
                if params:
                    subprocess.Popen(str(params[0]), shell=True, 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL)
            elif action == "open_url":
                if params:
                    webbrowser.open(str(params[0]))
            elif action == "mouse_click" and len(params) == 2:
                pyautogui.click(int(params[0]), int(params[1]))
        except Exception as e:
            print(f"    ❌ Ошибка шага {i}: {e}")

def main():
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    print("🤖 Бот Red OS (исправленная версия)")
    print("Ctrl+C или 'exit' для выхода")
    
    while True:
        try:
            user_input = input("\n> Задача: ").strip()
            if user_input.lower() in ["exit", "quit", "выход"]:
                print("👋 До свидания!")
                sys.exit(0)
            if not user_input:
                continue

            # Разделение по номерам задач (1., 2. и т.д.)
            tasks = re.split(r'(\d+\.\s+)', user_input)
            tasks = [t.strip() for t in tasks if t.strip() and not re.match(r'^\d+\.$', t.strip())]

            for idx, task in enumerate(tasks, 1):
                print(f"\n📋 Подзадача {idx}/{len(tasks)}: {task}")
                
                commands = get_ai_instruction(task)
                if commands:
                    execute_command_list(commands)
                    time.sleep(0.5)  # Пауза для обновления UI
                    trigger_screen_script()
                else:
                    print(f"[-] Не удалось обработать: {task}")

        except KeyboardInterrupt:
            print("\n👋 Остановлено")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
