from .collaborative import CollaborativeFilteringRecommender
from .content_based import ContentBasedFilteringRecommender
from ..config import settings
import pandas as pd
import numpy as np
import json

class HybridRecommender:
    def __init__(self, alpha=None):
        self.alpha = alpha if alpha is not None else settings.ALPHA_WEIGHT
        self.collaborative = CollaborativeFilteringRecommender()
        self.content_based = ContentBasedFilteringRecommender()
        self.is_trained = False
    
    def train(self, interactions_df, products_df):
        """Train both collaborative and content-based models"""
        try:
            # Train collaborative filtering
            self.collaborative.train(interactions_df)
            
            # Build content-based feature vectors
            self.content_based.build_feature_vectors(products_df)
            
            self.is_trained = True
            print("✅ Hybrid recommender trained successfully")
        except Exception as e:
            print(f"❌ Error training hybrid recommender: {e}")
            self.is_trained = False
    
    def recommend_for_user(self, user_id, interactions_df, products_df, n_recommendations=20):
        """Get hybrid recommendations for a user"""
        if interactions_df.empty or products_df.empty:
            return self._get_fallback_recommendations(products_df, n_recommendations)

        self.train(interactions_df, products_df)
        
        try:
            user_interacted_products = set(
                interactions_df[interactions_df["user_id"] == user_id]["product_id"].tolist()
            )
            candidate_product_ids = [
                product_id for product_id in list(products_df["id"])
                if product_id not in user_interacted_products
            ]

            # Get collaborative recommendations
            collab_recs = self.collaborative.recommend_for_user(
                user_id, 
                candidate_product_ids,
                n_recommendations * 2
            )
            
            # Get content-based recommendations
            content_recs = self.content_based.recommend_for_user(
                user_id,
                interactions_df,
                products_df,
                n_recommendations * 2
            )
            
            # If content-based failed, fall back to collaborative only
            if not content_recs:
                print(f"ℹ️ Using collaborative-only recommendations for user {user_id}")
                collab_pairs = [
                    (rec["product_id"], rec.get("collaborative_score", 0))
                    for rec in collab_recs
                ]
                return self._format_recommendations(
                    collab_pairs[:n_recommendations],
                    products_df,
                    "Based on user behavior patterns"
                )
            
            # Create score dictionaries
            collab_scores = {r['product_id']: r.get('collaborative_score', 0) for r in collab_recs}
            content_scores = {r['product_id']: r.get('content_score', 0) for r in content_recs}
            
            # Get all product IDs
            all_product_ids = set(collab_scores.keys()) | set(content_scores.keys())
            
            if not all_product_ids:
                print(f"⚠️ No recommendations available for user {user_id}")
                return []
            
            # Normalize scores
            def normalize_scores(scores_dict):
                if not scores_dict:
                    return {}
                values = list(scores_dict.values())
                min_score = min(values)
                max_score = max(values)
                if max_score == min_score:
                    return {k: 0.5 for k in scores_dict}
                return {k: (v - min_score) / (max_score - min_score) for k, v in scores_dict.items()}
            
            norm_collab = normalize_scores(collab_scores)
            norm_content = normalize_scores(content_scores)
            
            # Calculate hybrid scores
            hybrid_scores = {}
            for product_id in all_product_ids:
                collab_score = norm_collab.get(product_id, 0)
                content_score = norm_content.get(product_id, 0)
                hybrid_scores[product_id] = (self.alpha * collab_score) + ((1 - self.alpha) * content_score)
            
            # Sort by hybrid score
            sorted_scores = sorted(
                hybrid_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Get top N recommendations
            top_products = sorted_scores[:n_recommendations]
            
            return self._format_recommendations(
                top_products,
                products_df,
                "Based on your preferences and similar users"
            )
            
        except Exception as e:
            print(f"❌ Error in hybrid recommendations: {e}")
            # Fall back to popular products
            return self._get_fallback_recommendations(products_df, n_recommendations)
    
    def _format_recommendations(self, recommendations, products_df, explanation):
        """Format recommendations with product details"""
        results = []
        for product_id, score in recommendations:
            try:
                product = products_df[products_df['id'] == product_id].iloc[0]
                product_dict = self._normalize_product_dict(product.to_dict())
                results.append({
                    'product': product_dict,
                    'score': float(score) if not isinstance(score, (int, float)) else score,
                    'explanation': explanation
                })
            except:
                continue
        return results
    
    def _get_fallback_recommendations(self, products_df, n_recommendations):
        """Fallback to popular products when recommendation fails"""
        popular = products_df.head(n_recommendations)
        results = []
        for _, product in popular.iterrows():
            results.append({
                'product': self._normalize_product_dict(product.to_dict()),
                'score': 0.5,
                'explanation': 'Popular products recommended'
            })
        return results
    
    def get_similar_products(self, product_id, products_df, n_similar=10):
        """Get similar products using content-based filtering"""
        if not self.content_based.is_trained:
            self.content_based.build_feature_vectors(products_df)
        similar = self.content_based.get_similar_products(product_id, n_similar)
        results = []
        for item in similar:
            try:
                product = products_df[products_df['id'] == item['product_id']].iloc[0]
                results.append(self._normalize_product_dict(product.to_dict()))
            except:
                continue
        return results

    def _normalize_product_dict(self, product):
        list_fields = ["style", "tags", "color", "size", "season"]
        for field in list_fields:
            value = product.get(field)
            if value is None or (isinstance(value, float) and pd.isna(value)):
                product[field] = []
            elif isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    product[field] = parsed if isinstance(parsed, list) else [str(parsed)]
                except json.JSONDecodeError:
                    product[field] = [value] if value else []
        numeric_defaults = {
            "rating": 0.0,
            "total_ratings": 0,
            "stock_quantity": 0,
        }
        for field, default in numeric_defaults.items():
            if product.get(field) is None or (isinstance(product.get(field), float) and pd.isna(product.get(field))):
                product[field] = default
        return product
