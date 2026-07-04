from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    preferred_categories = Column(JSON, default=list)
    preferred_styles = Column(JSON, default=list)
    preferred_price_min = Column(Float, default=0)
    preferred_price_max = Column(Float, default=100000)
    location = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    interactions = relationship("Interaction", back_populates="user", cascade="all, delete-orphan")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(50), nullable=False, index=True)
    sub_category = Column(String(50), index=True)
    gender = Column(String(20))
    style = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    price = Column(Float, nullable=False, index=True)
    discount_price = Column(Float)
    currency = Column(String(3), default="NPR")
    color = Column(JSON, default=list)
    size = Column(JSON, default=list)
    brand = Column(String(100))
    material = Column(String(100))
    season = Column(JSON, default=list)
    image_url = Column(Text)
    thumbnail_url = Column(Text)
    stock_quantity = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    interactions = relationship("Interaction", back_populates="product", cascade="all, delete-orphan")

class Interaction(Base):
    __tablename__ = "interactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    interaction_type = Column(String(20), nullable=False)
    weight = Column(Float, default=1.0)
    rating_value = Column(Integer)
    session_id = Column(String(100))
    device_type = Column(String(50))
    browser = Column(String(100))
    os = Column(String(100))
    time_spent = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="interactions")
    product = relationship("Product", back_populates="interactions")