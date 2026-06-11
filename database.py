import sqlite3
from datetime import datetime

DB_NAME = 'ansible_runs.db'

def get_connection():
    # Подключаемся к базе. row_factory позволяет обращаться к колонкам по имени: row['user']
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    # Создаем таблицу, если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            playbook_name TEXT NOT NULL,
            user TEXT NOT NULL,
            status TEXT NOT NULL,
            start_time DATETIME NOT NULL,
            end_time DATETIME NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def get_runs(start_date=None, end_date=None, user=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM runs WHERE 1=1"
    params = []

    # Динамически собираем SQL-запрос в зависимости от переданных фильтров
    if start_date:
        query += " AND start_time >= ?"
        params.append(start_date)
    if end_date:
        query += " AND end_time <= ?"
        params.append(end_date)
    if user:
        query += " AND user = ?"
        params.append(user)
        
    query += " ORDER BY start_time DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    # Преобразуем объекты БД в обычные словари для JSON
    return [dict(row) for row in rows]