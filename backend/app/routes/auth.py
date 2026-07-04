from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User
from ..schemas import UserRegister, UserLogin, Token
from ..security import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, get_current_user
)
import uuid

def normalize_username(username: str) -> str:
    return username.strip()

def normalize_email(email: str) -> str:
    return email.strip().lower()

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    username = normalize_username(user_data.username)
    email = normalize_email(user_data.email)
    print(
        "[AUTH] Register request "
        f"username={username} email={email} "
        f"categories={user_data.preferred_categories or []} "
        f"styles={user_data.preferred_styles or []} "
        f"location={user_data.location}"
    )

    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        print(f"[AUTH] Register failed: duplicate username/email for {username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    new_user = User(
        id=str(uuid.uuid4()),
        username=username,
        email=email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name.strip() if user_data.first_name else None,
        last_name=user_data.last_name.strip() if user_data.last_name else None,
        preferred_categories=user_data.preferred_categories or [],
        preferred_styles=user_data.preferred_styles or [],
        preferred_price_min=user_data.preferred_price_min or 0,
        preferred_price_max=user_data.preferred_price_max or 100000,
        location=user_data.location
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    print(
        "[AUTH] Registered user "
        f"id={new_user.id} username={new_user.username} "
        f"name={new_user.first_name or ''} {new_user.last_name or ''}"
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": new_user.username})
    refresh_token = create_refresh_token(data={"sub": new_user.username})
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    login_id = normalize_username(user_data.username)
    print(f"[AUTH] Login attempt username_or_email={login_id}")
    
    user = db.query(User).filter(
        (User.username == login_id) | (User.email == login_id.lower())
    ).first()
    
    if not user:
        print(f"[AUTH] Login failed: user not found username_or_email={login_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not verify_password(user_data.password, user.password_hash):
        print(f"[AUTH] Login failed: incorrect password username={user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Upgrade any old plaintext development passwords to a hash after a
    # successful fallback verification.
    if not user.password_hash.startswith("$2"):
        user.password_hash = get_password_hash(user_data.password)
        db.commit()
        print(f"[AUTH] Upgraded plaintext development password hash username={user.username}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    print(f"[AUTH] Login success username={user.username} user_id={user.id}")
    
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/logout")
def logout():
    # Client-side will remove tokens
    return {"message": "Successfully logged out"}

# REMOVED: @router.get("/me") - moved to users router
