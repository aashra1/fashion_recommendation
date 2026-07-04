from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserUpdate, UserResponse
from ..security import get_current_user

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name
    if user_update.preferred_categories is not None:
        current_user.preferred_categories = user_update.preferred_categories
    if user_update.preferred_styles is not None:
        current_user.preferred_styles = user_update.preferred_styles
    if user_update.preferred_price_min is not None:
        current_user.preferred_price_min = user_update.preferred_price_min
    if user_update.preferred_price_max is not None:
        current_user.preferred_price_max = user_update.preferred_price_max
    if user_update.location is not None:
        current_user.location = user_update.location
    
    db.commit()
    db.refresh(current_user)
    return current_user