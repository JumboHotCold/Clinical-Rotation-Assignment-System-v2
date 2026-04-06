
import sqlite3
import pprint

def check_schema():
    conn = sqlite3.connect('clinical_rotation.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    
    schema = {}
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        schema[table] = [col[1] for col in columns]
    
    pprint.pprint(schema)
    conn.close()

if __name__ == "__main__":
    check_schema()
