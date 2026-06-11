import sqlite3
import random
import os
from datetime import datetime, timedelta
from database import init_db, get_connection

init_db()

playbook_dir = 'playbooks'
playbooks = [f for f in os.listdir(playbook_dir) if f.endswith('.yml') or f.endswith('.yaml')]

complexity_fail_rates = {
    '03_k8s_workers.yml': 40,
    '02_docker_stack.yml': 20,
    '04_database_backup.yml': 25,
    '01_nginx_advanced.yml': 15,
    '05_secure_ssh.yml': 5,
    '06_create_users.yml': 2
}

# Редкие фамилии и сервисные аккаунты
users = {
    'v.proskuryakov': 1.0, 
    'd.yaguzhinsky': 0.7, 
    't.bessoltsev': 1.5, 
    's.rastorguev': 0.8,
    'gitlab-runner': 0.4,
    'jenkins-agent': 0.4
}

conn = get_connection()
cursor = conn.cursor()
now = datetime.now()

cursor.execute("DELETE FROM runs")

for _ in range(50): 
    p_book = random.choice(playbooks)
    user = random.choice(list(users.keys()))
    
    base_fail_rate = complexity_fail_rates.get(p_book, 10)
    final_fail_rate = min(base_fail_rate * users[user], 95)
    
    if random.uniform(0, 100) < final_fail_rate:
        status = 'FAILED'
    else:
        status = 'SUCCESS'
    
    start_time = now - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
    end_time = start_time + timedelta(minutes=random.randint(1, 15), seconds=random.randint(0, 59))
    
    cursor.execute('''
        INSERT INTO runs (playbook_name, user, status, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    ''', (p_book, user, status, start_time.strftime('%Y-%m-%d %H:%M:%S'), end_time.strftime('%Y-%m-%d %H:%M:%S')))

conn.commit()
conn.close()