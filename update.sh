#!/bin/bash

# Скрипт автоматической установки и обновления для body1-2.py и screen-2.py на Red OS

set -e  # Остановка при ошибке

echo "🔄 Обновление системы Red OS..."
sudo dnf clean all
sudo dnf update -y

echo "🐍 Установка актуальной версии Python 3 и инструментов разработки..."
sudo dnf install -y python3 python3-pip python3-devel python3-setuptools gcc gcc-c++ make

echo "🎨 Установка tkinter и графических зависимостей..."
sudo dnf install -y python3-tkinter tk-devel tcl-devel libX11-devel libXext-devel libXrender-devel

echo "📦 Установка системных зависимостей для PyAutoGUI и MSS..."
sudo dnf install -y python3-xlib scrot libjpeg-turbo-devel libpng-devel

echo "🔧 Создание виртуального окружения для изоляции зависимостей..."
python3 -m venv /opt/project_env
source /opt/project_env/bin/activate

echo "📥 Обновление pip и установка Python библиотек..."
pip install --upgrade pip setuptools wheel

# Зависимости для body1-2.py
pip install pyautogui requests

# Зависимости для screen-2.py
pip install mss python-docx pillow

# Дополнительные зависимости для стабильности
pip install numpy opencv-python

echo "✅ Проверка установленных пакетов:"
pip list | grep -E "(pyautogui|requests|mss|docx|pillow|nump|opencv)"

echo "💾 Сохранение скрипта активации окружения..."
cat > ~/activate_project.sh << 'EOF'
#!/bin/bash
source /opt/project_env/bin/activate
echo "✅ Виртуальное окружение активировано"
EOF
chmod +x ~/activate_project.sh

echo "🚀 Создание лаунчера для запуска скриптов..."
cat > ~/run_body1.sh << 'EOF'
#!/bin/bash
source /opt/project_env/bin/activate
cd ~ && python3 body1-2.py
EOF

cat > ~/run_screen.sh << 'EOF'
#!/bin/bash
source /opt/project_env/bin/activate
cd ~ && python3 screen-2.py
EOF

chmod +x ~/run_body1.sh ~/run_screen.sh

echo "✅ УСТАНОВКА ЗАВЕРШЕНА!"
echo ""
echo "🔗 Для запуска:"
echo "  source ~/activate_project.sh          # Активация окружения"
echo "  или"
echo "  ~/run_body1.sh                        # Запуск body1-2.py"
echo "  ~/run_screen.sh                       # Запуск screen-2.py"
echo ""
echo "📁 Файлы размещены в:"
echo "  • Виртуальное окружение: /opt/project_env/"
echo "  • Скрипты запуска: ~/run_*.sh"[file:1][file:2][file:3][web:4][web:10][web:11]

## Основные улучшения

Скрипт теперь выполняет полное обновление системы, устанавливает Python в виртуальное окружение для изоляции зависимостей и добавляет удобные лаунчеры. Все пакеты dnf устанавливаются через официальные репозитории Red OS, а pip-пакеты — в изолированном окружении.[file:1][web:4][web:12]

## Тестирование установки

После запуска выполните:
