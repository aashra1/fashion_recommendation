from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import json
import logging

logger = logging.getLogger("fashion_recommender.content_based")

class ContentBasedFilteringRecommender:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            min_df=1
        )
        self.tfidf_matrix = None
        self.product_ids = None
        self.product_features = None
        self.is_trained = False

    def _to_list(self, value):
        if value is None:
            return []
        if isinstance(value, float) and pd.isna(value):
            return []
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                return parsed if isinstance(parsed, list) else [str(parsed)]
            except json.JSONDecodeError:
                return [value]
        return [str(value)]
    
    def build_feature_vectors(self, products_df):
        """Build TF-IDF vectors from product attributes"""
        if products_df.empty:
            print("[CONTENT_BASED] ⚠️ No products found to build feature vectors")
            return
        
        print(f"[CONTENT_BASED] 🛠️ Building TF-IDF Feature Space for {len(products_df)} products...")
        features = []
        
        for _, product in products_df.iterrows():
            text_parts = [
                str(product.get('name', '')),
                str(product.get('category', '')),
                str(product.get('sub_category', '')),
                str(product.get('gender', '')),
                str(product.get('brand', '')),
                str(product.get('material', ''))
            ]
            
            style = self._to_list(product.get('style', []))
            text_parts.extend([str(s) for s in style])
            
            tags = self._to_list(product.get('tags', []))
            text_parts.extend([str(t) for t in tags])
            
            feature_text = ' '.join(str(part) for part in text_parts if part and str(part) != 'nan')
            features.append(feature_text)
        
        if all(not f.strip() for f in features):
            print("[CONTENT_BASED] ⚠️ All product features empty. Falling back to product names.")
            features = [str(p.get('name', f'Product_{i}')) for i, p in products_df.iterrows()]
        
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(features)
            self.product_ids = list(products_df['id'])
            self.product_features = features
            self.is_trained = True
            
            vocab_size = len(self.tfidf_vectorizer.vocabulary_)
            print(f"[CONTENT_BASED] ✅ TF-IDF Model Trained! Vector matrix shape: {self.tfidf_matrix.shape} (Products x Terms), Vocabulary size: {vocab_size}")
        except Exception as e:
            print(f"[CONTENT_BASED] ❌ Error building TF-IDF feature vectors: {e}")
            self.is_trained = False
    
    def get_similar_products(self, product_id, n_similar=10):
        """Get products similar to a given product using Cosine Similarity"""
        if not self.is_trained or self.tfidf_matrix is None:
            print("[CONTENT_BASED] ⚠️ Model not trained for similar products query")
            return []
        
        try:
            idx = self.product_ids.index(product_id)
        except ValueError:
            print(f"[CONTENT_BASED] ⚠️ Product ID {product_id} not found in feature matrix")
            return []
        
        product_vector = self.tfidf_matrix[idx]
        similarities = cosine_similarity(product_vector, self.tfidf_matrix).flatten()
        
        if hasattr(similarities, 'A'):
            similarities = similarities.A1
        
        similar_indices = similarities.argsort()[::-1]
        similar_indices = [i for i in similar_indices if i != idx][:n_similar]
        
        results = []
        for i in similar_indices:
            results.append({
                'product_id': self.product_ids[i],
                'similarity_score': float(similarities[i])
            })
        
        print(f"[CONTENT_BASED] 🔍 Similar products computed for Item ID {product_id}: Top similarity = {results[0]['similarity_score']:.4f} if results else 0")
        return results

    def recommend_from_profile_text(self, profile_text, candidate_products, products_df, n_recommendations=20):
        """Build a vector from user preference profile text (Cold-start Users)"""
        if not self.is_trained or self.tfidf_matrix is None or not profile_text.strip():
            return []
        
        print(f"[CONTENT_BASED] 👤 Constructing Profile Vector from user explicit preferences: '{profile_text}'")
        try:
            profile_vector = self.tfidf_vectorizer.transform([profile_text])
            scores = []
            
            for product_id in candidate_products:
                if product_id in self.product_ids:
                    idx = self.product_ids.index(product_id)
                    p_vec = self.tfidf_matrix[idx]
                    sim = float(cosine_similarity(profile_vector, p_vec)[0][0])
                    scores.append({
                        'product_id': product_id,
                        'content_score': sim
                    })
            
            scores.sort(key=lambda x: x['content_score'], reverse=True)
            print(f"[CONTENT_BASED] 📊 Profile text recommendation generated {len(scores)} candidate scores. Max similarity = {scores[0]['content_score']:.4f}" if scores else "[CONTENT_BASED] No candidate scores.")
            return scores[:n_recommendations]
        except Exception as e:
            print(f"[CONTENT_BASED] ❌ Error scoring profile text: {e}")
            return []

    def recommend_for_user(self, user_id, interactions_df, products_df, n_recommendations=20):
        """Get content-based recommendations for an existing user based on interaction history"""
        if not self.is_trained or self.tfidf_matrix is None:
            print("[CONTENT_BASED] ⚠️ Model not trained")
            return []
        
        user_interactions = interactions_df[interactions_df['user_id'] == user_id]
        user_products = user_interactions['product_id'].tolist()
        
        if not user_products:
            print(f"[CONTENT_BASED] ℹ️ User {user_id} has 0 interaction items in dataset")
            return []
        
        all_product_ids = list(products_df['id'])
        candidate_products = [p for p in all_product_ids if p not in user_products]
        
        if not candidate_products:
            print(f"[CONTENT_BASED] ℹ️ No un-interacted candidate products for User {user_id}")
            return []
        
        # Build user profile vector by weighting interacted product vectors
        user_vector = None
        count = 0
        
        for _, row in user_interactions.iterrows():
            product_id = row['product_id']
            weight = row.get('weight', 1.0)
            try:
                idx = self.product_ids.index(product_id)
                vector = self.tfidf_matrix[idx] * weight
                if user_vector is None:
                    user_vector = vector.copy()
                else:
                    user_vector = user_vector + vector
                count += weight
            except ValueError:
                continue
        
        if user_vector is None or count == 0:
            print(f"[CONTENT_BASED] ⚠️ Unable to form valid user vector for User {user_id}")
            return []
        
        user_vector = user_vector / count
        
        print(f"[CONTENT_BASED] 🧠 User TF-IDF Vector computed from {len(user_products)} interacted items (Total weight: {count:.2f})")
        
        scores = []
        for product_id in candidate_products:
            try:
                idx = self.product_ids.index(product_id)
                product_vector = self.tfidf_matrix[idx]
                similarity = float(cosine_similarity(user_vector, product_vector)[0][0])
                
                scores.append({
                    'product_id': product_id,
                    'content_score': similarity
                })
            except Exception as e:
                continue
        
        scores.sort(key=lambda x: x['content_score'], reverse=True)
        print(f"[CONTENT_BASED] 🎯 Ranked {len(scores)} candidate products using TF-IDF Cosine Similarity for User {user_id}. Top score: {scores[0]['content_score']:.4f}" if scores else "[CONTENT_BASED] No candidate products ranked.")
        return scores[:n_recommendations]
