from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import json

class ContentBasedFilteringRecommender:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            min_df=1  # Changed from 2 to 1 to avoid empty matrix
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
            print("⚠️ No products found to build feature vectors")
            return
        
        # Create text features by combining product attributes
        features = []
        
        for _, product in products_df.iterrows():
            # Combine all text attributes
            text_parts = [
                str(product.get('name', '')),
                str(product.get('category', '')),
                str(product.get('sub_category', '')),
                str(product.get('gender', '')),
                str(product.get('brand', '')),
                str(product.get('material', ''))
            ]
            
            # Add style and tags
            style = self._to_list(product.get('style', []))
            text_parts.extend([str(s) for s in style])
            
            tags = self._to_list(product.get('tags', []))
            text_parts.extend([str(t) for t in tags])
            
            # Join all parts
            feature_text = ' '.join(str(part) for part in text_parts if part and str(part) != 'nan')
            features.append(feature_text)
        
        # Create TF-IDF matrix - handle case where all features are empty
        if all(not f.strip() for f in features):
            print("⚠️ All product features are empty. Using default features.")
            # Use product names as fallback
            features = [str(p.get('name', f'Product_{i}')) for i, p in products_df.iterrows()]
        
        try:
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(features)
            self.product_ids = list(products_df['id'])
            self.product_features = features
            self.is_trained = True
            print(f"✅ Content-based model trained with {len(features)} products")
        except Exception as e:
            print(f"❌ Error building feature vectors: {e}")
            self.is_trained = False
    
    def get_similar_products(self, product_id, n_similar=10):
        """Get products similar to a given product"""
        if not self.is_trained or self.tfidf_matrix is None:
            print("⚠️ Content-based model not trained")
            return []
        
        # Find product index
        try:
            idx = self.product_ids.index(product_id)
        except ValueError:
            print(f"⚠️ Product {product_id} not found in content-based model")
            return []
        
        # Get product vector
        product_vector = self.tfidf_matrix[idx]
        
        # Calculate cosine similarity - convert to numpy array to avoid matrix issues
        similarities = cosine_similarity(product_vector, self.tfidf_matrix).flatten()
        
        # Convert to numpy array if it's a matrix
        if hasattr(similarities, 'A'):
            similarities = similarities.A1
        
        # Get top N similar products (excluding self)
        similar_indices = similarities.argsort()[::-1]
        similar_indices = [i for i in similar_indices if i != idx][:n_similar]
        
        results = []
        for i in similar_indices:
            results.append({
                'product_id': self.product_ids[i],
                'similarity_score': float(similarities[i])
            })
        
        return results
    
    def recommend_for_user(self, user_id, interactions_df, products_df, n_recommendations=20):
        """Get content-based recommendations for a user"""
        if not self.is_trained or self.tfidf_matrix is None:
            print("⚠️ Content-based model not trained")
            return []
        
        # Get user's interacted products
        user_interactions = interactions_df[interactions_df['user_id'] == user_id]
        user_products = user_interactions['product_id'].tolist()
        
        if not user_products:
            print(f"ℹ️ User {user_id} has no interactions for content-based recommendations")
            return []
        
        # Get products the user hasn't interacted with
        all_product_ids = list(products_df['id'])
        candidate_products = [p for p in all_product_ids if p not in user_products]
        
        if not candidate_products:
            print(f"ℹ️ No candidate products for user {user_id}")
            return []
        
        # Get user's profile vector (average of interacted product vectors)
        user_vector = None
        count = 0
        
        for product_id in user_products:
            try:
                idx = self.product_ids.index(product_id)
                vector = self.tfidf_matrix[idx]
                if user_vector is None:
                    user_vector = vector.copy()
                else:
                    user_vector = user_vector + vector
                count += 1
            except ValueError:
                continue
        
        if user_vector is None or count == 0:
            print(f"ℹ️ No valid product vectors for user {user_id}")
            return []
        
        # Average the vectors
        user_vector = user_vector / count
        
        # Calculate similarity for candidate products
        scores = []
        for product_id in candidate_products:
            try:
                idx = self.product_ids.index(product_id)
                product_vector = self.tfidf_matrix[idx]
                similarity = cosine_similarity(user_vector, product_vector)
                similarity_value = float(similarity[0][0])
                
                scores.append({
                    'product_id': product_id,
                    'content_score': similarity_value
                })  
            except Exception as e:
                print(f"⚠️ Error calculating similarity for product {product_id}: {e}")
                continue
        
        # Sort by similarity
        scores.sort(key=lambda x: x['content_score'], reverse=True)
        return scores[:n_recommendations]
