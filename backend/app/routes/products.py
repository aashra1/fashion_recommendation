from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func, desc
from ..database import get_db
from ..models import Product, Interaction
from ..schemas import ProductResponse
from typing import List, Optional

router = APIRouter(prefix="/api/products", tags=["products"])

def split_filter(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]

def json_array_contains_any(column, values: list[str]):
    conditions = [column.like(f'%"{value}"%') for value in values]
    return or_(*conditions) if conditions else None

@router.get("/popular", response_model=List[ProductResponse])
@router.get("/popular/", response_model=List[ProductResponse])
def get_popular_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get popular products based on total interaction weight."""
    products = db.query(
        Product,
        func.coalesce(func.sum(Interaction.weight), 0).label("total_weight")
    ).outerjoin(Interaction).group_by(Product.id).order_by(
        desc("total_weight"),
        Product.created_at.desc()
    ).limit(limit).all()

    return [product for product, _ in products]

@router.get("/trending", response_model=List[ProductResponse])
@router.get("/trending/", response_model=List[ProductResponse])
def get_trending_products(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get trending products from the last N days, with popular products as fallback."""
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    products = db.query(
        Product,
        func.count(Interaction.id).label("interaction_count")
    ).outerjoin(Interaction).filter(
        or_(Interaction.created_at >= cutoff_date, Interaction.id.is_(None))
    ).group_by(Product.id).order_by(
        desc("interaction_count"),
        Product.created_at.desc()
    ).limit(limit).all()

    return [product for product, _ in products]

@router.get("/", response_model=List[ProductResponse])
def get_products(
    category: Optional[str] = None,
    sub_category: Optional[str] = None,
    gender: Optional[str] = None,
    style: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "popularity",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    # Apply filters
    categories = split_filter(category)
    sub_categories = split_filter(sub_category)
    genders = split_filter(gender)
    styles = split_filter(style)

    if categories:
        query = query.filter(Product.category.in_(categories))
    if sub_categories:
        query = query.filter(Product.sub_category.in_(sub_categories))
    if genders:
        query = query.filter(Product.gender.in_(genders))
    if styles:
        query = query.filter(json_array_contains_any(Product.style, styles))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term),
                Product.brand.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == "popularity":
        query = query.outerjoin(Interaction).group_by(Product.id).order_by(
            func.count(Interaction.id).desc()
        )
    elif sort_by == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort_by == "newest":
        query = query.order_by(Product.created_at.desc())
    else:
        query = query.order_by(Product.created_at.desc())
    
    # Pagination
    offset = (page - 1) * page_size
    products = query.offset(offset).limit(page_size).all()
    
    return products

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
