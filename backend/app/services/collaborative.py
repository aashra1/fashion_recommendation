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
        """Train SVD model on interaction data"""
        reader = Reader(rating_scale=(0.5, 2.0))
        
        # Prepare data for Surprise
        data = Dataset.load_from_df(
            interactions_df[['user_id', 'product_id', 'weight']],
            reader
        )
        
        # Train the model
        self.model = SVD(
            n_factors=self.n_factors,
            n_epochs=self.n_epochs,
            lr_all=self.lr_all,
            reg_all=self.reg_all
        )
        
        trainset = data.build_full_trainset()
        self.model.fit(trainset)
        
        # Store user and product IDs
        self.user_ids = set(interactions_df['user_id'].unique())
        self.product_ids = set(interactions_df['product_id'].unique())
        self.is_trained = True
    
    def predict_rating(self, user_id, product_id):
        """Predict rating for a user-product pair"""
        if not self.is_trained:
            return 1.0
        
        try:
            return self.model.predict(user_id, product_id).est
        except:
            return 1.0
    
    def recommend_for_user(self, user_id, product_ids, n_recommendations=20):
        """Get top N recommendations for a user"""
        if not self.is_trained:
            return []
        
        predictions = []
        for product_id in product_ids:
            rating = self.predict_rating(user_id, product_id)
            predictions.append({
                'product_id': product_id,
                'collaborative_score': rating
            })
        
        # Sort by rating
        predictions.sort(key=lambda x: x['collaborative_score'], reverse=True)
        return predictions[:n_recommendations]
    
    def save_model(self, filepath):
        """Save model to disk"""
        if self.model:
            with open(filepath, 'wb') as f:
                pickle.dump(self.model, f)
    
    def load_model(self, filepath):
        """Load model from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                self.model = pickle.load(f)
                self.is_trained = True