
import json
from backend.database import SessionLocal
from backend import schemas, models
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import joinedload

def test_routes():
    db = SessionLocal()
    try:
        print("--- Testing /students/ ---")
        students_data = db.query(models.Student).all()
        if not students_data:
            print("No students in DB.")
        else:
            try:
                TypeAdapter(list[schemas.Student]).validate_python(students_data)
                print("Students validation: OK")
            except ValidationError as e:
                print(f"Students validation FAILED: {e.errors()}")
        
        print("\n--- Testing /assignments/ ---")
        # Try with joinedload to see if it fixes the 'missing student' error
        assignments_data = db.query(models.Assignment).options(
            joinedload(models.Assignment.student),
            joinedload(models.Assignment.area)
        ).all()
        
        if not assignments_data:
            print("No assignments in DB.")
        else:
            try:
                TypeAdapter(list[schemas.Assignment]).validate_python(assignments_data)
                print("Assignments validation (with joinedload): OK")
            except ValidationError as e:
                print(f"Assignments validation (with joinedload) FAILED: {e.errors()}")
                
    finally:
        db.close()

if __name__ == "__main__":
    test_routes()
