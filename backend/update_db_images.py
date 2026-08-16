import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Product

image_updates = {
    "Daura Suruwal Set": "https://images.unsplash.com/photo-1617137968427-85924c800a22?w=600&auto=format&fit=crop",
    "Kurta Suruwal": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop",
    "Casual Denim Jacket": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop",
    "Saree Collection": "https://images.unsplash.com/photo-1610030469983-98e550d6193c?w=600&auto=format&fit=crop",
    "Mountain Trekking Gear": "https://images.unsplash.com/photo-1551698618-1dfe5d97d256?w=600&auto=format&fit=crop",
    "Kids Festival Dress": "https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?w=600&auto=format&fit=crop",
    "Pashmina Shawl": "https://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=600&auto=format&fit=crop",
    "Men's Formal Blazer": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=600&auto=format&fit=crop",
    "Yoga Wear Set": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=600&auto=format&fit=crop",
    "Traditional Newari Topi": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=600&auto=format&fit=crop",
    "Leather Boots": "https://images.unsplash.com/photo-1638247025967-b4e38f787b76?w=600&auto=format&fit=crop",
    "Baby Cotton Set": "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=600&auto=format&fit=crop",
    "Dhaka Topi Collection": "https://images.unsplash.com/photo-1606760227091-3dd870d97f1d?w=600&auto=format&fit=crop",
    "Designer Bridal Saree": "https://images.unsplash.com/photo-1617627143750-d86bc21e42bb?w=600&auto=format&fit=crop",
    "Hiking Backpack": "https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600&auto=format&fit=crop",
    "Winter Beanie Set": "https://images.unsplash.com/photo-1576871337632-b9aef4c17ab9?w=600&auto=format&fit=crop",
    "School Uniform Set": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600&auto=format&fit=crop"
}

def update_images():
    db = SessionLocal()
    try:
        updated_count = 0
        for name, new_url in image_updates.items():
            products = db.query(Product).filter(Product.name == name).all()
            for p in products:
                p.image_url = new_url
                updated_count += 1
        db.commit()
        print(f"✅ Successfully updated product images in SQLite DB ({updated_count} records updated).")
    except Exception as e:
        db.rollback()
        print(f"❌ Error updating database images: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_images()
