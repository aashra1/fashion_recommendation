import json
from datetime import datetime, timedelta
from ..config import settings

class RecommendationCache:
    def __init__(self):
        # Simple in-memory cache (Redis not required)
        self.cache = {}
        self.default_ttl = 3600  # 1 hour
    
    def get_recommendations(self, user_id):
        """Get cached recommendations for a user"""
        cache_key = f"rec:{user_id}"
        
        if cache_key in self.cache:
            cache_entry = self.cache[cache_key]
            # Check if cache is still valid
            if datetime.utcnow() < cache_entry['expires_at']:
                return cache_entry['data']
            else:
                del self.cache[cache_key]
        
        return None
    
    def set_recommendations(self, user_id, recommendations, ttl=3600):
        """Cache recommendations for a user"""
        cache_key = f"rec:{user_id}"
        expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self.cache[cache_key] = {
            'data': recommendations,
            'expires_at': expires_at
        }
    
    def invalidate_user(self, user_id):
        """Invalidate cache for a specific user"""
        cache_key = f"rec:{user_id}"
        if cache_key in self.cache:
            del self.cache[cache_key]
    
    def clear_all(self):
        """Clear all cache"""
        self.cache.clear()