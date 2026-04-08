from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import schemas, crud, models
from ..auth import get_db, get_current_user, get_current_admin_user

router = APIRouter(prefix="/areas", tags=["areas"])

@router.post("/", response_model=schemas.ClinicalArea)
def create_clinical_area(area: schemas.ClinicalAreaCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    return crud.create_clinical_area(db=db, area=area)

@router.get("/", response_model=List[schemas.ClinicalArea])
def read_areas(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return crud.get_clinical_areas(db)

@router.get("/{area_id}/students", response_model=schemas.AreaStudentsSchedule)
def get_area_students(area_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Get all students assigned to a specific area, grouped by their schedule.
    - Admins can see all students in any area
    - Students can only see students in areas they're assigned to
    """
    # Get the area data
    area_data = crud.get_students_by_area(db, area_id)
    
    if not area_data:
        raise HTTPException(status_code=404, detail="Area not found")
    
    # Check permissions for students
    if current_user.role == "student":
        # Students can only view areas they're assigned to
        student = db.query(models.Student).filter(models.Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=403, detail="Not authorized")
        
        # Check if this student has any assignment in this area
        has_assignment = db.query(models.Assignment).filter(
            models.Assignment.student_id == student.id,
            models.Assignment.area_id == area_id,
            models.Assignment.status == "Active"
        ).first()
        
        if not has_assignment:
            raise HTTPException(status_code=403, detail="You don't have access to this area")
    
    return area_data

@router.put("/{area_id}", response_model=schemas.ClinicalArea)
def update_area(area_id: int, updates: schemas.ClinicalAreaUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    area = crud.update_clinical_area(db, area_id, updates)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area

@router.delete("/{area_id}")
def delete_area(area_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    success = crud.delete_clinical_area(db, area_id)
    if not success:
        raise HTTPException(status_code=404, detail="Area not found")
    return {"detail": "Area deleted"}
