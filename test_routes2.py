import json
from backend.database import SessionLocal
from backend import schemas, models
from pydantic import TypeAdapter, ValidationError
from sqlalchemy.orm import joinedload

def test_routes():
    db = SessionLocal()
    try:
        with open('test_output_py.txt', 'w') as f:
            f.write("--- Testing /students/ ---\n")
            students_data = db.query(models.Student).all()
            if not students_data:
                f.write("No students in DB.\n")
            else:
                try:
                    TypeAdapter(list[schemas.Student]).validate_python(students_data)
                    f.write("Students validation: OK\n")
                except ValidationError as e:
                    f.write(f"Students validation FAILED:\n{e}\n")
            
            f.write("\n--- Testing /assignments/ ---\n")
            assignments_data = db.query(models.Assignment).options(
                joinedload(models.Assignment.student),
                joinedload(models.Assignment.area)
            ).all()
            
            if not assignments_data:
                f.write("No assignments in DB.\n")
            else:
                try:
                    TypeAdapter(list[schemas.Assignment]).validate_python(assignments_data)
                    f.write("Assignments validation (with joinedload): OK\n")
                except ValidationError as e:
                    f.write(f"Assignments validation (with joinedload) FAILED:\n{e}\n")
    finally:
        db.close()

if __name__ == "__main__":
    test_routes()
