#!/bin/bash

# Скрипт для обновления RedOS, установки Python и необходимых библиотек
# Запускать: chmod +x update.sh && ./update.sh

echo "--- Начинаю обновление системы RedOS ---"
sudo dnf update -y

echo "--- Установка инструментов разработки и системных зависимостей ---"
# Эти зависимости нужны для сборки некоторых библиотек (например, pyautogui)
sudo dnf install -y python3 python3-pip python3-devel \
    gcc gcc-c++ make \
    libX11-devel libXtst-devel libpng-devel \
    python3-tkinter scrot

echo "--- Обновление pip до последней версии ---"
python3 -m pip install --upgrade pip

echo "--- Установка необходимых Python-библиотек ---"
# Стандартные библиотеки (os, sys, time, re, json, subprocess, webbrowser) 
# уже встроены в Python и не требуют установки.

# Устанавливаем внешние зависимости
python3 -m pip install \
    requests \
    pyautogui \
    mss \
    python-docx

echo "--- Готово! Система и окружение настроены. ---"
