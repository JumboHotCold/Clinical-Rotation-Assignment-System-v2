from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models
from ..auth import get_db, get_current_user, get_current_admin_user

router = APIRouter(prefix="/students", tags=["students"])

@router.post("/", response_model=schemas.Student)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    db_user = crud.get_user_by_username(db, username=student.student_id_number)
    if db_user:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    return crud.create_student(db=db, student=student)

@router.get("/", response_model=List[schemas.Student])
def read_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_students(db, skip=skip, limit=limit)

@router.put("/{student_id}", response_model=schemas.Student)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    student = crud.update_student(db, student_id, updates)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    success = crud.delete_student(db, student_id)
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted"}
