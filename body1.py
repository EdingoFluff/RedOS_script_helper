import json
import time
import pyautogui
import requests
import subprocess
import webbrowser
import re

# --- КОНФИГУРАЦИЯ API ---
API_KEY = ""
BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "kwaipilot/kat-coder-pro:free"

# Упрощенный промпт (без лишней нагрузки на AI)
SYSTEM_PROMPT = """
Ты — модуль управления Red OS. Возвращай ТОЛЬКО валидный JSON-список команд для конкретной задачи.

**Действия:**
- "hotkey": ["ctrl","alt","t"]
- "type": ["текст"]
- "wait": [2]
- "run_shell": ["команда"]
- "open_url": ["url"]
- "mouse_click": [x, y]

**Правила Red OS:**
- Рабочий стол: /home/sergeykos/Desktop
- Всегда выполняй работы в новом окне терминала
- Терминал: ctrl+alt+t → type → enter
- Команды: dnf вместо apt
- Админ: su - → enter → пароль "1"
- Минимум 1 команда, максимум 500
- НИКОГДА не [] или текст
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
            {"role": "user", "content": f"Выполни задачу: {user_text}"},
        ],
        "temperature": 0.1,
    }

    for attempt in range(max_retries):
        try:
            resp = requests.post(BASE_URL, headers=headers, json=payload, timeout=30)
            if resp.status_code == 429:
                time.sleep(2 ** (attempt + 1))
                continue
            
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"].strip()
            # Очистка от markdown-оберток, если AI их добавит
            content = re.sub(r'```json|```', '', content).strip()
            return json.loads(content)
        except Exception as e:
            print(f"[-] Ошибка AI: {e}")
    return None

def trigger_screen_script():
    """Автоматический вызов скрипта документирования."""
    print("[*] Фиксация выполнения (screen.py)...")
    try:
        subprocess.Popen(["python3", "screen.py"])
    except Exception as e:
        print(f"[-] Не удалось запустить screen.py: {e}")

def execute_command_list(command_list: list):
    for i, command_json in enumerate(command_list):
        action = command_json.get("action")
        params = command_json.get("params", [])
        
        try:
            if action == "hotkey":
                pyautogui.hotkey(*params)
            elif action == "type":
                pyautogui.write(" ".join(map(str, params)), interval=0.01)
            elif action == "wait":
                time.sleep(float(params[0]) if params else 1.0)
            elif action == "run_shell":
                subprocess.Popen(" ".join(map(str, params)), shell=True)
            elif action == "open_url":
                webbrowser.open(params[0])
            elif action == "mouse_click":
                pyautogui.click(params[0], params[1])
        except Exception as e:
            print(f"❌ Ошибка на шаге {i+1}: {e}")

def main():
    pyautogui.FAILSAFE = True
    print("🤖 Бот-управленец Red OS (Оптимизированный).")
    
    while True:
        try:
            user_input = input("\n> Введите список задач: ").strip()
            if user_input.lower() in ["exit", "quit", "выход"]: break
            if not user_input: continue

            # Разделяем сложный ввод на отдельные инструкции
            # Ищем паттерны типа "1.", "2." или просто перенос строки
            tasks = re.split(r'\d+\.\s+', user_input)
            tasks = [t.strip() for t in tasks if t.strip()]

            for index, task in enumerate(tasks):
                print(f"\n[Обработка подзадачи {index+1}/{len(tasks)}]: {task}")
                
                command_list = get_ai_instruction(task)
                
                if command_list:
                    execute_command_list(command_list)
                    # Делаем небольшую паузу, чтобы интерфейс ОС успел обновиться
                    time.sleep(1) 
                    # Сами запускаем скриншот после каждой подзадачи
                    trigger_screen_script()
                else:
                    print(f"[-] Пропуск задачи '{task}' из-за ошибки AI.")

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
