import json
import time
import pyautogui
import requests
import subprocess
import webbrowser

# --- КОНФИГУРАЦИЯ API ---
API_KEY = ""
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "kwaipilot/kat-coder-pro:free"

SYSTEM_PROMPT = """
Ты — модуль управления Red OS. Возвращай ТОЛЬКО валидный JSON-список команд.

**Действия:**
- "hotkey": ["ctrl","alt","t"] или ["enter"]
- "type": ["текст"] (один элемент)
- "wait": [2] (пауза 2 сек перед каждой командой)
- "run_shell": ["firefox"] (без терминала)
- "open_url": ["https://ya.ru"]
- "mouse_click": [100,500]

**Правила Red OS:**
- Рабочий стол: /home/sergeykos/Desktop
- Всегда выполняй работы в новом окне терминала
- Терминал: ctrl+alt+t → type → enter
- Команды: dnf вместо apt
- Админ: su - → enter → пароль "1"
- Воспринимай каждый пункт (1. 2.) как отдельную инструкцию
- В КОНЦЕ каждой инструкции: python3 screen.py через run_shell
- Минимум 1 команда, максимум 500
- НИКОГДА не [] или текст

Примеры:
"Папка data": [{"action":"hotkey","params":["ctrl","alt","t"]},{"action":"wait","params":[2]},{"action":"type","params":["mkdir ~/data"]},{"action":"hotkey","params":["enter"]},{"action":"run_shell","params":["python3 screen.py"]},{"action":"hotkey","params":["enter"]}]
"Яндекс": [{"action":"open_url","params":["https://ya.ru"]}]
"""

def get_ai_instruction(user_text: str, max_retries: int = 4) -> list | None:
    """Получает список JSON-команд от AI с повторными попытками."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "temperature": 0.1,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
            
            if resp.status_code == 429:
                wait_time = 2 ** (attempt + 1)
                print(f"[-] Ошибка 429. Попытка {attempt + 1}/{max_retries}. Ожидание {wait_time}с...")
                time.sleep(wait_time)
                continue
            
            print(f"[HTTP] {resp.status_code}")
            resp.raise_for_status()

            content = resp.json()["choices"][0]["message"]["content"].strip()
            return json.loads(content)

        except requests.exceptions.RequestException as e:
            print(f"[-] HTTP ошибка: {e}")
        except json.JSONDecodeError as e:
            print(f"[-] JSON ошибка: {e}")
            print(f"[-] Получено: {content[:200]}...")
            if attempt < max_retries - 1:
                continue
        except Exception as e:
            print(f"[-] Ошибка: {e}")
    
    return None

def execute_command_list(command_list: list):
    """Выполняет последовательность команд."""
    for i, command_json in enumerate(command_list):
        action = command_json.get("action")
        params = command_json.get("params", [])
        
        print(f"[*] Шаг {i+1}/{len(command_list)}: {action} {params}")

        try:
            if action == "hotkey":
                pyautogui.hotkey(*params)
                
            elif action == "type":
                text = " ".join(map(str, params))
                pyautogui.write(text, interval=0.01)
                
            elif action == "wait":
                t = float(params[0]) if params else 2.0
                time.sleep(t)
                
            elif action == "run_shell":
                if params:
                    cmd = " ".join(map(str, params))
                    print(f"   [RUN] {cmd}")
                    subprocess.Popen(cmd, shell=True)
                    
            elif action == "open_url":
                if params:
                    webbrowser.open(params[0])
                    
            elif action == "mouse_click":
                if len(params) >= 2:
                    pyautogui.click(params[0], params[1])
            else:
                print(f"[-] Неизвестное действие: {action}")
        
        except Exception as e:
            print(f"❌ Ошибка шага {i+1}: {e}")
            break

def main():
    """Основной цикл программы."""
    pyautogui.FAILSAFE = True
    print("🤖 Бот-управленец Red OS запущен.")
    print(f"[*] Модель: {MODEL}")
    print("Введите команды или 'выйти' для завершения.")
    
    while True:
        try:
            user_input = input("\n> Что сделать? ").strip()
            
            if user_input.lower() in ["выйти", "выход", "exit", "quit"]:
                print("👋 До свидания!")
                break
            
            if not user_input:
                continue

            command_list = get_ai_instruction(user_input)
            
            if isinstance(command_list, list):
                print(f"[AI] {len(command_list)} команд получено.")
                time.sleep(1)
                execute_command_list(command_list)
            else:
                print("[-] Не удалось получить команды.")
                
        except KeyboardInterrupt:
            print("\n👋 Остановлено.")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()

