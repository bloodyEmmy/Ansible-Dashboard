import sqlite3

DB_NAME = 'ansible_runs.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
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

def get_runs(start_date=None, end_date=None, user=None, playbook=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM runs WHERE 1=1"
    params = []

    if start_date:
        query += " AND start_time >= ?"
        params.append(start_date)
    if end_date:
        query += " AND end_time <= ?"
        params.append(end_date)
    if user:
        query += " AND user LIKE ?"
        params.append(f"%{user}%")
    if playbook:
        query += " AND playbook_name LIKE ?"
        params.append(f"%{playbook}%")
        
    query += " ORDER BY start_time DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]