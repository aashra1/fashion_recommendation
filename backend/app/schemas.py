from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_categories: Optional[List[str]] = Field(default_factory=list)
    preferred_styles: Optional[List[str]] = Field(default_factory=list)
    preferred_price_min: Optional[float] = 0
    preferred_price_max: Optional[float] = 100000
    location: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    preferred_categories: List[str]
    preferred_styles: List[str]
    preferred_price_min: float
    preferred_price_max: float
    location: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_categories: Optional[List[str]] = None
    preferred_styles: Optional[List[str]] = None
    preferred_price_min: Optional[float] = None
    preferred_price_max: Optional[float] = None
    location: Optional[str] = None

# Product Schemas
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    sub_category: Optional[str] = None
    gender: Optional[str] = None
    style: Optional[List[str]] = Field(default_factory=list)
    tags: Optional[List[str]] = Field(default_factory=list)
    price: float
    discount_price: Optional[float] = None
    currency: str = "NPR"
    color: Optional[List[str]] = Field(default_factory=list)
    size: Optional[List[str]] = Field(default_factory=list)
    brand: Optional[str] = None
    material: Optional[str] = None
    season: Optional[List[str]] = Field(default_factory=list)
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    stock_quantity: int = 0

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    rating: float
    total_ratings: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Interaction Schemas
class InteractionLog(BaseModel):
    product_id: str
    interaction_type: str  # VIEW, CLICK, WISHLIST_ADD, CART_ADD, PURCHASE, RATING
    rating_value: Optional[int] = None
    time_spent: Optional[int] = None
    device_type: Optional[str] = None
    browser: Optional[str] = None
    os: Optional[str] = None

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    product: ProductResponse
    score: float
    explanation: Optional[str] = None
