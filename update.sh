#!/bin/bash
# Скрипт автоматической установки зависимостей для body1.py и screen.py на Red OS

# Обновление системы
sudo dnf update -y

# Установка системных пакетов Python и pip
sudo dnf install -y python3 python3-pip python3-devel gcc

# Установка библиотек для body1.py
pip3 install pyautogui requests

# Установка библиотек для screen.py
pip3 install mss python-docx pillow

sudo dnf install -y python3-tkinter tk-devel

sudo dnf install -y python3-devel gcc python3-pip

# Проверка установки
echo "Проверка установленных пакетов:"
pip3 list | grep -E "(pyautogui|requests|mss|docx|pillow)"

echo "Установка завершена! Все зависимости установлены."

