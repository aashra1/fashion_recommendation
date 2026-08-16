from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..database import get_db
from ..models import User, Product, Interaction
from ..schemas import ProductResponse, RecommendationResponse
from ..security import get_current_user
from ..services.hybrid import HybridRecommender
from ..services.cache import RecommendationCache
import pandas as pd

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])
recommender = HybridRecommender()
cache = RecommendationCache()

def products_dataframe(db: Session) -> pd.DataFrame:
    return pd.read_sql(db.query(Product).statement, db.bind)

def popular_products(db: Session, limit: int):
    products = db.query(
        Product,
        func.coalesce(func.sum(Interaction.weight), 0).label("total_weight")
    ).outerjoin(Interaction).group_by(Product.id).order_by(
        desc("total_weight"),
        Product.created_at.desc()
    ).limit(limit).all()
    return [product for product, _ in products]

def recommendations_from_products(products, explanation: str):
    return [
        {"product": product, "score": 0.5, "explanation": explanation}
        for product in products
    ]

def hydrate_recommendations(db: Session, recommendations):
    product_ids = [
        rec.get("product", {}).get("id")
        for rec in recommendations
        if rec.get("product") and rec.get("product", {}).get("id")
    ]
    if not product_ids:
        return []

    products = db.query(Product).filter(Product.id.in_(product_ids)).all()
    product_map = {product.id: product for product in products}
    hydrated = []
    for rec in recommendations:
        product_id = rec.get("product", {}).get("id")
        product = product_map.get(product_id)
        if product:
            hydrated.append({
                "product": product,
                "score": float(rec.get("score", 0.0)),
                "explanation": rec.get("explanation")
            })
    return hydrated

@router.get("/personalized", response_model=list[RecommendationResponse])
def get_personalized_recommendations(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    print(f"\n[RECOMMENDATION_API]: GET /api/recommendations/personalized for User: '{current_user.username}' (ID: {current_user.id})")
    
    # Check cache first
    cached = cache.get_recommendations(current_user.id)
    if cached:
        print(f"[CACHE] ⚡ Cache HIT for User ID: {current_user.id}. Returning cached recommendation feed.")
        hydrated_cached = hydrate_recommendations(db, cached)
        if hydrated_cached:
            return hydrated_cached[:limit]
    
    print(f"[CACHE]  Cache MISS for User ID: {current_user.id}. Executing Recommendation Engine...")
    
    all_interactions = db.query(Interaction).all()
    print(f"[DATASET] 📈 Total Interactions in DB: {len(all_interactions)}")
    
    # Prepare data for recommendation
    if all_interactions:
        interactions_df = pd.DataFrame([{
            'user_id': i.user_id,
            'product_id': i.product_id,
            'weight': i.weight
        } for i in all_interactions])
    else:
        interactions_df = pd.DataFrame(columns=['user_id', 'product_id', 'weight'])
    
    products_df = products_dataframe(db)
    print(f"[DATASET] Total Products in DB: {len(products_df)}")
    
    # Get recommendations via Hybrid Engine
    recommendations = recommender.recommend_for_user(
        current_user,
        interactions_df,
        products_df,
        limit
    )
    
    if not recommendations:
        print(f"[RECOMMENDATION_API] ℹ️ Returning fallback popular products for User: {current_user.username}")
        return recommendations_from_products(
            popular_products(db, limit),
            "Popular fashion items"
        )

    # Cache results
    cache.set_recommendations(current_user.id, recommendations)
    print(f"[CACHE] 💾 Cached {len(recommendations)} recommendation items for User ID: {current_user.id}")
    
    hydrated = hydrate_recommendations(db, recommendations)
    print(f"[RECOMMENDATION_API] Returning {len(hydrated)} personalized items for User: {current_user.username}\n")

    return hydrated or recommendations_from_products(
        popular_products(db, limit),
        "Popular fashion items"
    )

@router.get("/similar/{product_id}", response_model=list[ProductResponse])
def get_similar_products(
    product_id: str,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    print(f"\n[RECOMMENDATION_API]  GET /api/recommendations/similar/{product_id}")
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        print(f"[RECOMMENDATION_API]  Product ID {product_id} not found!")
        raise HTTPException(status_code=404, detail="Product not found")
    
    print(f"[RECOMMENDATION_API] 🔎 Finding products similar to: '{product.name}' ({product.category} - {product.sub_category})")
    products_df = products_dataframe(db)
    similar = recommender.get_similar_products(product_id, products_df, limit + 1)
    
    similar_ids = [p["id"] for p in similar if p.get("id") != product_id][:limit]
    if not similar_ids:
        print(f"[RECOMMENDATION_API] ⚠️ No similar products found. Returning popular fallback.")
        return [
            p for p in popular_products(db, limit + 1)
            if p.id != product_id
        ][:limit]

    products = db.query(Product).filter(Product.id.in_(similar_ids)).all()
    product_map = {product.id: product for product in products}
    results = [product_map[pid] for pid in similar_ids if pid in product_map]
    print(f"[RECOMMENDATION_API] Found {len(results)} similar products for '{product.name}'\n")
    return results
