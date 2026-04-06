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
