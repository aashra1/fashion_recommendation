import sys
import os

# Add backend directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import Product

image_updates = {
    "Daura Suruwal Set": "http://127.0.0.1:8000/assets/images/daura-suruwal.jpg",
    "Kurta Suruwal": "http://127.0.0.1:8000/assets/images/kurta-suruwal.jpg",
    "Casual Denim Jacket": "http://127.0.0.1:8000/assets/images/denim-jacket.jpg",
    "Saree Collection": "http://127.0.0.1:8000/assets/images/saree.jpg",
    "Mountain Trekking Gear": "http://127.0.0.1:8000/assets/images/trekking-gear.jpg",
    "Kids Festival Dress": "http://127.0.0.1:8000/assets/images/kids-festival-dress.jpg",
    "Pashmina Shawl": "http://127.0.0.1:8000/assets/images/pashmina-shawl.jpg",
    "Men's Formal Blazer": "http://127.0.0.1:8000/assets/images/formal-blazer.jpg",
    "Yoga Wear Set": "http://127.0.0.1:8000/assets/images/yoga-wear.jpg",
    "Traditional Newari Topi": "http://127.0.0.1:8000/assets/images/newari-topi.jpg",
    "Leather Boots": "http://127.0.0.1:8000/assets/images/leather-boots.jpg",
    "Baby Cotton Set": "http://127.0.0.1:8000/assets/images/baby-cotton-set.jpg",
    "Dhaka Topi Collection": "http://127.0.0.1:8000/assets/images/dhaka-topi.jpg",
    "Designer Bridal Saree": "http://127.0.0.1:8000/assets/images/bridal-saree.jpg",
    "Hiking Backpack": "http://127.0.0.1:8000/assets/images/hiking-backpack.jpg",
    "Winter Beanie Set": "http://127.0.0.1:8000/assets/images/winter-beanie.jpg",
    "School Uniform Set": "http://127.0.0.1:8000/assets/images/school-uniform.jpg"
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
        print(f" Successfully updated product images in SQLite DB ({updated_count} records updated).")
    except Exception as e:
        db.rollback()
        print(f" Error updating database images: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    update_images()
