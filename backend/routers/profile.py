from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas, crud, models
from ..auth import get_db, get_current_user

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/me", response_model=schemas.User)
def get_my_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/settings", response_model=schemas.User)
def update_my_profile(
    updates: schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return crud.update_user_profile(db, user_id=current_user.id, updates=updates)

@router.put("/change-password", response_model=schemas.User)
def change_my_password(
    password_data: schemas.UserPasswordUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify current password
    if not crud.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    return crud.update_user_password(db, user_id=current_user.id, new_password=password_data.new_password)
