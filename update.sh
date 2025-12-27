#!/bin/bash

# Остановить выполнение при ошибке
set -e

echo "--- 1. Обновление системы ---"
sudo dnf update -y

echo "--- 2. Установка Python и базовых инструментов разработки ---"
# Red OS обычно поставляется с Python 3, но нам нужны заголовки для сборки библиотек
sudo dnf install -y python3 python3-pip python3-devel gcc gcc-c++

echo "--- 3. Установка системных зависимостей для PyAutoGUI и MSS ---"
# PyAutoGUI требует библиотеку для работы с X11 и Tkinter
# MSS требует библиотеку для работы с экраном
sudo dnf install -y \
    python3-tkinter \
    libX11-devel \
    libXtst-devel \
    libpng-devel \
    libjpeg-devel \
    scrot

echo "--- 4. Обновление pip и установка Python-библиотек ---"
python3 -m pip install --user --upgrade pip

# Установка библиотек, указанных в ваших файлах
python3 -m pip install --user \
    mss \
    python-docx \
    pyautogui \
    requests

echo "--- 5. Проверка установки ---"
python3 -c "import mss; import docx; import pyautogui; import requests; print('✅ Все библиотеки успешно импортированы!')"

echo "-------------------------------------------------------"
echo "Настройка завершена!"
echo "ВАЖНО: Для работы PyAutoGUI убедитесь, что вы используете X11 (не Wayland)."
echo "Чтобы запустить бота, выполните: python3 body1.py"
