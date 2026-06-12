# Ansible Audit Dashboard

Система аудита и мониторинга запусков конфигурационных сценариев (Ansible Playbooks). Сервис считывает статистику из реляционной базы данных SQLite и предоставляет веб-интерфейс с дашбордами, а также REST API для получения сырых данных в формате JSON.

## Структура проекта
* `app.py` - серверная часть (Flask, API роуты, автоматическая генерация данных).
* `database.py` - логика взаимодействия с БД SQLite.
* `templates/` и `static/` - файлы frontend-части.
* `Dockerfile` - инструкции для сборки Docker-образа.
* `requirements.txt` - список Python-зависимостей.

## Запуск через Docker (Рекомендуемый способ)

1. Сборка Docker-образа:
    docker build -t ansible-dashboard .

2. Запуск контейнера в фоновом режиме:
    docker run -d -p 5000:5000 --name audit-dashboard ansible-dashboard

После запуска интерфейс доступен по адресу: http://127.0.0.1:5000

Для остановки контейнера:
    docker stop audit-dashboard

## Локальный запуск (Без Docker)

1. Создание виртуального окружения и установка зависимостей:
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

2. Запуск веб-сервера (при первом запуске БД и файлы сгенерируются автоматически):
    python app.py

## Использование REST API (cURL)

Сервер предоставляет конечные точки для интеграции. Для структурированного вывода JSON рекомендуется использовать утилиту jq.

Получить общую историю запусков:
    curl -s "http://127.0.0.1:5000/api/history" | jq

Отфильтровать данные по конкретному пользователю:
    curl -s "http://127.0.0.1:5000/api/history?user=v.proskuryakov" | jq

Отфильтровать по названию исполняемого файла сценария:
    curl -s "http://127.0.0.1:5000/api/history?playbook=02_docker_stack.yml" | jq

Комбинированный запрос (поиск по пользователю в заданном временном диапазоне):
    curl -s "http://127.0.0.1:5000/api/history?user=gitlab-runner&start_date=2026-05-01&end_date=2026-06-30" | jq

Прочитать исходный код конкретного сценария:
    curl -s "http://127.0.0.1:5000/api/playbook/05_secure_ssh.yml" | jq