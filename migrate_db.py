
import sqlite3
from backend.models import Base
from backend.database import engine

def migrate():
    conn = sqlite3.connect('clinical_rotation.db')
    cursor = conn.cursor()
    
    # Get all tables from SQLAlchemy models
    for table_name, table in Base.metadata.tables.items():
        print(f"Checking table: {table_name}")
        
        # Get existing columns in the database
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_columns = {col[1] for col in cursor.fetchall()}
        
        # Check for missing columns
        for col_name, column in table.columns.items():
            if col_name not in existing_columns:
                print(f"  Adding column: {col_name} to {table_name}")
                
                # Determine type for SQLite
                col_type = str(column.type)
                if "VARCHAR" in col_type or "STRING" in col_type:
                    type_str = "TEXT"
                elif "INTEGER" in col_type:
                    type_str = "INTEGER"
                elif "BOOLEAN" in col_type:
                    type_str = "BOOLEAN"
                elif "DATETIME" in col_type:
                    type_str = "DATETIME"
                elif "DATE" in col_type:
                    type_str = "DATE"
                elif "TIME" in col_type:
                    type_str = "TIME"
                else:
                    type_str = "TEXT"
                
                # Default values
                default = ""
                if column.server_default is not None:
                    # In SQLite, we can't easily add a column with server_default for some cases
                    # but for func.now() we can use CURRENT_TIMESTAMP
                    if "now" in str(column.server_default.arg).lower():
                        default = " DEFAULT CURRENT_TIMESTAMP"
                elif column.default is not None:
                    if isinstance(column.default.arg, bool):
                        default = f" DEFAULT {1 if column.default.arg else 0}"
                    elif isinstance(column.default.arg, (int, float)):
                        default = f" DEFAULT {column.default.arg}"
                    elif isinstance(column.default.arg, str):
                        default = f" DEFAULT '{column.default.arg}'"
                
                try:
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {type_str}{default}")
                except Exception as e:
                    print(f"  Error adding {col_name}: {e}")
    
    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
