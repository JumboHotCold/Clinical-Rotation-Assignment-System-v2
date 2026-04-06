
import sqlite3

def migrate():
    conn = sqlite3.connect('clinical_rotation.db')
    cursor = conn.cursor()
    
    # Check if 'status' column exists in 'students'
    cursor.execute("PRAGMA table_info(students)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'status' not in columns:
        print("Adding 'status' column to 'students' table...")
        cursor.execute("ALTER TABLE students ADD COLUMN status TEXT DEFAULT 'Active'")
        conn.commit()
        print("Migration complete!")
    else:
        print("'status' column already exists.")
    
    conn.close()

if __name__ == "__main__":
    migrate()
