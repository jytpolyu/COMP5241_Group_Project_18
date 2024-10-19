import sqlite3

def init_db():
    conn = sqlite3.connect('github_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS commits (id INTEGER PRIMARY KEY, message TEXT, author TEXT)''')
    conn.commit()
    conn.close()

def get_commit_data(message=None, author=None):
    conn = sqlite3.connect('github_data.db')
    c = conn.cursor()
    
    if message and author:
        c.execute("INSERT INTO commits (message, author) VALUES (?, ?)", (message, author))
        conn.commit()
    
    c.execute("SELECT * FROM commits")
    rows = c.fetchall()
    conn.close()
    return rows
