import sqlite3

def init_db():
    conn = sqlite3.connect("ebooks.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS ebooks (
            id TEXT PRIMARY KEY,
            title TEXT,
            node_url TEXT,
            ext TEXT
        )
    """)

    conn.commit()
    conn.close()
