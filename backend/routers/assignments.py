from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models
from ..auth import get_db, get_current_user, get_current_admin_user

router = APIRouter(prefix="/assignments", tags=["assignments"])

@router.post("/", response_model=schemas.Assignment)
def create_assignment(assignment: schemas.AssignmentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    # Run Conflict Checker Engine
    conflict_check = crud.check_assignment_conflicts(db, assignment)
    if conflict_check["conflict"]:
        raise HTTPException(status_code=400, detail=conflict_check["message"])
    return crud.create_assignment(db, assignment)

@router.get("/", response_model=List[schemas.Assignment])
def read_assignments(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # In a full app, we might filter by the student if current_user is a student
    return crud.get_assignments(db)

@router.put("/{assignment_id}", response_model=schemas.Assignment)
def update_assignment(assignment_id: int, updates: schemas.AssignmentUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    assignment = crud.update_assignment(db, assignment_id, updates)
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.delete("/{assignment_id}")
def delete_assignment(assignment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    success = crud.delete_assignment(db, assignment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return {"detail": "Assignment deleted"}
