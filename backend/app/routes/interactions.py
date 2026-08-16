from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Interaction, User, Product
from ..schemas import InteractionLog
from ..security import get_current_user, get_weight_for_interaction
from ..routes.recommendations import cache
import uuid

router = APIRouter(prefix="/api/interactions", tags=["interactions"])

@router.post("/log")
def log_interaction(
    interaction: InteractionLog,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if product exists
    product = db.query(Product).filter(Product.id == interaction.product_id).first()
    if not product:
        print(f"[INTERACTION] ❌ Failed to log interaction. Product ID {interaction.product_id} not found.")
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate weight
    weight = get_weight_for_interaction(interaction.interaction_type, interaction.rating_value)
    device_type = interaction.device_type or "Unknown"
    
    # Create interaction
    new_interaction = Interaction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        product_id=interaction.product_id,
        interaction_type=interaction.interaction_type,
        weight=weight,
        rating_value=interaction.rating_value,
        device_type=device_type,
        browser=interaction.browser,
        os=interaction.os,
        time_spent=interaction.time_spent
    )
    
    db.add(new_interaction)
    db.commit()
    db.refresh(new_interaction)
    
    # Invalidate recommendation cache for user so next feed re-calculates
    cache.invalidate_user(current_user.id)
    print(f"[INTERACTION] 🖱️ User '{current_user.username}' -> Event: {interaction.interaction_type} on '{product.name}' (Weight: {weight}) | User Cache Invalidated!")
    
    return {"message": "Interaction logged successfully"}

@router.post("/batch-log")
def batch_log_interactions(
    interactions: list[InteractionLog],
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    count = 0
    for interaction in interactions:
        product = db.query(Product).filter(Product.id == interaction.product_id).first()
        if not product:
            continue
        
        weight = get_weight_for_interaction(interaction.interaction_type, interaction.rating_value)
        
        new_interaction = Interaction(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            product_id=interaction.product_id,
            interaction_type=interaction.interaction_type,
            weight=weight,
            rating_value=interaction.rating_value,
            device_type=interaction.device_type,
            browser=interaction.browser,
            os=interaction.os,
            time_spent=interaction.time_spent
        )
        db.add(new_interaction)
        count += 1
    
    db.commit()
    if count > 0:
        cache.invalidate_user(current_user.id)
        print(f"[INTERACTION] 📦 Batch logged {count} interactions for User '{current_user.username}' | Cache Invalidated!")
    
    return {"message": f"{count} interactions logged successfully"}