# Ansible Audit Dashboard

Система аудита и мониторинга запусков конфигурационных сценариев (Ansible Playbooks). Сервис считывает статистику из реляционной базы данных SQLite и предоставляет веб-интерфейс с дашбордами, а также REST API для получения сырых данных в формате JSON.

## Структура проекта
* `app.py` - серверная часть (Flask, API роуты).
* `database.py` - логика взаимодействия с БД SQLite.
* `mock_data.py` - скрипт генерации статистики запусков.
* `generate_playbooks.py` - генератор исходных файлов сценариев.
* `playbooks/` - директория с исходным кодом Ansible сценариев.
* `templates/` и `static/` - файлы frontend-части.
* `requirements.txt` - список Python-зависимостей.

## Развертывание и запуск

1. Создание виртуального окружения и установка зависимостей:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt