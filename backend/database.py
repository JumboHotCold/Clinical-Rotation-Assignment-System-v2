from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

logger = logging.getLogger(__name__)

SQLALCHEMY_DATABASE_URL = "sqlite:///./clinical_rotation.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Enable foreign key support for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def ensure_schema_columns():
    """Ensure all required columns exist in tables. Adds missing columns."""
    from . import models
    
    inspector = inspect(engine)
    
    tables_to_check = {
        "users": ["created_at", "updated_at", "must_change_password", "profile_picture"],
        "clinical_areas": ["created_at", "updated_at"],
        "assignments": ["date_assigned", "created_at", "updated_at"],
        "attendance_records": ["created_at", "updated_at"],
    }
    
    with engine.connect() as conn:
        for table_name, required_columns in tables_to_check.items():
            if not inspector.has_table(table_name):
                continue
                
            existing_columns = {col["name"] for col in inspector.get_columns(table_name)}
            
            for col_name in required_columns:
                if col_name not in existing_columns:
                    logger.info(f"Adding missing column '{col_name}' to table '{table_name}'")
                    
                    # Default values based on column type
                    if col_name in ["created_at", "updated_at", "date_assigned"]:
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} DATETIME DEFAULT CURRENT_TIMESTAMP"
                    elif col_name == "must_change_password":
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} BOOLEAN DEFAULT 0"
                    elif col_name == "profile_picture":
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} TEXT DEFAULT NULL"
                    else:
                        continue
                    
                    try:
                        conn.execute(text(sql))
                        conn.commit()
                        logger.info(f"✓ Successfully added column '{col_name}' to '{table_name}'")
                    except Exception as e:
                        logger.warning(f"Column '{col_name}' may already exist or error occurred: {e}")
                        conn.rollback()
        
        conn.close()
