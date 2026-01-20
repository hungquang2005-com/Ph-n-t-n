import sqlite3

conn = sqlite3.connect("ebooks.db")
c = conn.cursor()

for row in c.execute("SELECT * FROM ebooks"):
    print(row)

conn.close()
