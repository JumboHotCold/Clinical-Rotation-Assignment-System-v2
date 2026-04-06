from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, time

from .. import schemas, crud, models
from ..auth import get_db, get_current_user

router = APIRouter(prefix="/attendance", tags=["attendance"])

@router.get("/", response_model=List[schemas.AttendanceRecord])
def read_attendance(student_id: int = None, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # If student, force them to only see their own attendance
    if current_user.role == "student":
        student_id = current_user.student_profile.id
    return crud.get_attendance_records(db, student_id)

@router.post("/clock-in", response_model=schemas.AttendanceRecord)
def clock_in(assignment_id: int, date_val: date, time_in: time, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Basic check - does assignment belong to this student?
    if current_user.role == "student":
        assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
        if not assignment or assignment.student_id != current_user.student_profile.id:
            raise HTTPException(status_code=403, detail="Not your assignment")

    return crud.clock_in(db, assignment_id, date_val, time_in)

@router.post("/clock-out", response_model=schemas.AttendanceRecord)
def clock_out(assignment_id: int, date_val: date, time_out: time, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    if current_user.role == "student":
        assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
        if not assignment or assignment.student_id != current_user.student_profile.id:
            raise HTTPException(status_code=403, detail="Not your assignment")

    return crud.clock_out(db, assignment_id, date_val, time_out)
