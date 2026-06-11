import sqlite3
import random
from datetime import datetime, timedelta
from database import init_db, get_connection

# Инициализируем пустую базу
init_db()

playbooks = ['geerlingguy.docker', 'nginx_setup.yml', 'deploy_k8s_nodes.yml', 'update_packages.yml']
users = ['m.trikhunkov', 'devops_intern', 'system_auto']
statuses = ['SUCCESS', 'SUCCESS', 'SUCCESS', 'FAILED'] # Вероятность успеха выше

conn = get_connection()
cursor = conn.cursor()

# Генерируем 15 случайных запусков за последние 7 дней
now = datetime.now()
for _ in range(15):
    p_book = random.choice(playbooks)
    user = random.choice(users)
    status = random.choice(statuses)
    
    # Генерируем случайное время старта
    start_time = now - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
    # Длительность прокатки от 1 до 15 минут
    end_time = start_time + timedelta(minutes=random.randint(1, 15))
    
    cursor.execute('''
        INSERT INTO runs (playbook_name, user, status, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (p_book, user, status, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
conn.close()

print("База данных успешно заполнена тестовыми прокатками!")