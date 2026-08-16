from surprise import SVD, Dataset, Reader
import pandas as pd
import pickle
import os

class CollaborativeFilteringRecommender:
    def __init__(self, n_factors=100, n_epochs=30, lr_all=0.005, reg_all=0.02):
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr_all = lr_all
        self.reg_all = reg_all
        self.model = None
        self.user_ids = None
        self.product_ids = None
        self.is_trained = False
    
    def train(self, interactions_df):
        """Train SVD model on user interaction weights"""
        if interactions_df.empty:
            print("[COLLABORATIVE] ⚠️ Interactions dataframe is empty. SVD model training skipped.")
            return

        print(f"[COLLABORATIVE] ⚙️ Training SVD Matrix Factorization Model (n_factors={self.n_factors}, n_epochs={self.n_epochs}, lr={self.lr_all}, reg={self.reg_all})...")
        
        # Scaling weights from 0.5 to 2.0
        min_w = interactions_df['weight'].min() if not interactions_df.empty else 0.5
        max_w = interactions_df['weight'].max() if not interactions_df.empty else 2.0
        reader = Reader(rating_scale=(min_w, max_w))
        
        data = Dataset.load_from_df(
            interactions_df[['user_id', 'product_id', 'weight']],
            reader
        )
        
        self.model = SVD(
            n_factors=self.n_factors,
            n_epochs=self.n_epochs,
            lr_all=self.lr_all,
            reg_all=self.reg_all
        )
        
        trainset = data.build_full_trainset()
        self.model.fit(trainset)
        
        self.user_ids = set(interactions_df['user_id'].unique())
        self.product_ids = set(interactions_df['product_id'].unique())
        self.is_trained = True
        
        print(f"[COLLABORATIVE] ✅ SVD Model Trained Successfully! Trainset size: {trainset.n_ratings} ratings across {trainset.n_users} users and {trainset.n_items} products.")
    
    def predict_rating(self, user_id, product_id):
        """Predict rating/interaction weight for a user-product pair using SVD decomposition"""
        if not self.is_trained or self.model is None:
            return 1.0
        
        try:
            prediction = self.model.predict(user_id, product_id)
            return float(prediction.est)
        except Exception as e:
            return 1.0
    
    def recommend_for_user(self, user_id, product_ids, n_recommendations=20):
        """Get top N collaborative SVD recommendations for a user"""
        if not self.is_trained or not product_ids:
            print(f"[COLLABORATIVE] ℹ️ Collaborative model not trained or no candidate product IDs for User {user_id}")
            return []
        
        is_known_user = user_id in self.user_ids
        print(f"[COLLABORATIVE] 🔍 Predicting SVD ratings for User {user_id} across {len(product_ids)} candidate items (Known user: {is_known_user})...")
        
        predictions = []
        for product_id in product_ids:
            rating = self.predict_rating(user_id, product_id)
            predictions.append({
                'product_id': product_id,
                'collaborative_score': rating
            })
        
        predictions.sort(key=lambda x: x['collaborative_score'], reverse=True)
        top_score = predictions[0]['collaborative_score'] if predictions else 0.0
        print(f"[COLLABORATIVE] 🎯 Top SVD score for User {user_id}: {top_score:.4f}")
        return predictions[:n_recommendations]
    
    def save_model(self, filepath):
        """Save model to disk"""
        if self.model:
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
            print(f"[COLLABORATIVE] 💾 SVD model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load model from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
                self.is_trained = True
            print(f"[COLLABORATIVE] 📂 SVD model loaded from {filepath}")