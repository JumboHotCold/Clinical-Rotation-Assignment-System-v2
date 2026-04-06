from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_db, get_current_admin_user

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin_user)):
    total_students = db.query(models.Student).count()
    total_areas = db.query(models.ClinicalArea).count()
    active_assignments = db.query(models.Assignment).filter(models.Assignment.status == "Active").count()
    
    return {
        "total_students": total_students,
        "total_areas": total_areas,
        "active_assignments": active_assignments
    }
