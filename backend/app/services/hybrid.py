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
        """Train both collaborative (SVD) and content-based (TF-IDF) models"""
        try:
            print(f"[HYBRID_ENGINE] Training Hybrid Recommender (Alpha Weight α={self.alpha:.2f})...")
            self.collaborative.train(interactions_df)
            self.content_based.build_feature_vectors(products_df)
            self.is_trained = True
            print("[HYBRID_ENGINE] Hybrid Recommender successfully trained both SVD and TF-IDF models!")
        except Exception as e:
            print(f"[HYBRID_ENGINE] Error training hybrid recommender: {e}")
            self.is_trained = False
    
    def recommend_for_user(self, user, interactions_df, products_df, n_recommendations=20):
        """Get hybrid recommendations for a user (or user profile)"""
        user_id = user.id if hasattr(user, 'id') else str(user)
        
        if interactions_df.empty or products_df.empty:
            print(f"[HYBRID_ENGINE] ⚠️ Dataset empty. Returning popular fallback products for User {user_id}")
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

            print(f"[HYBRID_ENGINE] Processing Hybrid Feed for User ID: {user_id}")
            print(f"[HYBRID_ENGINE] Prior interactions logged: {len(user_interacted_products)} items | Candidate pool: {len(candidate_product_ids)} items")

            # Check if user has zero interactions (Cold-Start)
            if not user_interacted_products:
                print(f"[HYBRID_ENGINE] ❄️ Cold-Start User detected! Attempting Profile-Based TF-IDF matching...")
                categories = getattr(user, 'preferred_categories', []) or []
                styles = getattr(user, 'preferred_styles', []) or []
                
                profile_terms = []
                if isinstance(categories, list):
                    profile_terms.extend(categories)
                if isinstance(styles, list):
                    profile_terms.extend(styles)
                
                profile_text = " ".join(profile_terms).strip()
                if profile_text:
                    print(f"[HYBRID_ENGINE] Matching candidates against user explicit profile tags: '{profile_text}'")
                    content_recs = self.content_based.recommend_from_profile_text(
                        profile_text,
                        candidate_product_ids,
                        products_df,
                        n_recommendations
                    )
                    if content_recs:
                        profile_pairs = [(rec["product_id"], rec["content_score"]) for rec in content_recs]
                        return self._format_recommendations(
                            profile_pairs,
                            products_df,
                            f"Based on your profile preferences ({', '.join(profile_terms)})"
                        )

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
                print(f"[HYBRID_ENGINE] Content-based model produced 0 results. Falling back to SVD Collaborative-only feed.")
                collab_pairs = [
                    (rec["product_id"], rec.get("collaborative_score", 0))
                    for rec in collab_recs
                ]
                return self._format_recommendations(
                    collab_pairs[:n_recommendations],
                    products_df,
                    "Based on user behavior patterns (Collaborative SVD)"
                )
            
            # Create score dictionaries
            collab_scores = {r['product_id']: r.get('collaborative_score', 0) for r in collab_recs}
            content_scores = {r['product_id']: r.get('content_score', 0) for r in content_recs}
            
            all_candidate_ids = set(collab_scores.keys()) | set(content_scores.keys())
            
            if not all_candidate_ids:
                print(f"[HYBRID_ENGINE] No candidate recommendations generated for User {user_id}")
                return self._get_fallback_recommendations(products_df, n_recommendations)
            
            # Normalize scores to [0, 1] range
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
            
            # Calculate hybrid weighted score: S_hybrid = α * S_collab + (1 - α) * S_content
            hybrid_scores = {}
            for product_id in all_candidate_ids:
                collab_score = norm_collab.get(product_id, 0.5)
                content_score = norm_content.get(product_id, 0.5)
                score = (self.alpha * collab_score) + ((1 - self.alpha) * content_score)
                hybrid_scores[product_id] = score
            
            sorted_scores = sorted(
                hybrid_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            top_products = sorted_scores[:n_recommendations]
            
            print(f"[HYBRID_ENGINE] Composite Hybrid Recommendations generated!")
            print(f"[HYBRID_ENGINE] Score Formula: S_hybrid = {self.alpha:.2f} * S_collab + {(1-self.alpha):.2f} * S_content")
            print(f"[HYBRID_ENGINE] Top #1 Item ID: {top_products[0][0]} | Score: {top_products[0][1]:.4f}" if top_products else "")
            
            return self._format_recommendations(
                top_products,
                products_df,
                "Tailored specifically for you using SVD Collaborative + TF-IDF Content Hybrid AI"
            )
            
        except Exception as e:
            print(f"[HYBRID_ENGINE] Error in hybrid recommendation computation: {e}")
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
            except Exception as e:
                continue
        return results
    
    def _get_fallback_recommendations(self, products_df, n_recommendations):
        """Fallback to popular products when recommendation fails or data is insufficient"""
        popular = products_df.head(n_recommendations)
        results = []
        for _, product in popular.iterrows():
            results.append({
                'product': self._normalize_product_dict(product.to_dict()),
                'score': 0.5,
                'explanation': 'Popular fashion items'
            })
        return results
    
    def get_similar_products(self, product_id, products_df, n_similar=10):
        """Get similar products using content-based filtering"""
        print(f"[HYBRID_ENGINE] Querying Similar Products for Item ID: {product_id}")
        if not self.content_based.is_trained:
            self.content_based.build_feature_vectors(products_df)
        similar = self.content_based.get_similar_products(product_id, n_similar)
        results = []
        for item in similar:
            try:
                product = products_df[products_df['id'] == item['product_id']].iloc[0]
                results.append(self._normalize_product_dict(product.to_dict()))
            except Exception as e:
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
