from sqlalchemy.orm import Session
from .models import User, Product, Interaction
from .security import get_password_hash
import uuid
import random

def seed_database(db: Session):
    """Seed the database with sample products and demo interactions"""
    
    # Check if products already exist
    if db.query(Product).count() > 0:
        print("✅ Products already exist, skipping seed...")
        return
    
    print("🌱 Seeding database with sample products...")
    
    # ============================================
    # NOTE: We're NOT creating seed users anymore!
    # Real users will register themselves.
    # Only creating 3 demo users for testing interactions
    # ============================================
    
    # Create demo users (for testing recommendations)
    demo_users = [
        User(
            id=str(uuid.uuid4()),
            username="demo_ram",
            email="demo_ram@email.com",
            password_hash=get_password_hash("demo123"),
            first_name="Ram",
            last_name="Shrestha",
            preferred_categories=["Men", "Traditional"],
            preferred_styles=["Casual", "Formal"],
            preferred_price_min=500,
            preferred_price_max=5000,
            location="Kathmandu"
        ),
        User(
            id=str(uuid.uuid4()),
            username="demo_sita",
            email="demo_sita@email.com",
            password_hash=get_password_hash("demo123"),
            first_name="Sita",
            last_name="Dahal",
            preferred_categories=["Women", "Kids"],
            preferred_styles=["Casual", "Traditional"],
            preferred_price_min=1000,
            preferred_price_max=8000,
            location="Pokhara"
        ),
        User(
            id=str(uuid.uuid4()),
            username="demo_hari",
            email="demo_hari@email.com",
            password_hash=get_password_hash("demo123"),
            first_name="Hari",
            last_name="Gurung",
            preferred_categories=["Men"],
            preferred_styles=["Sport", "Casual"],
            preferred_price_min=2000,
            preferred_price_max=10000,
            location="Biratnagar"
        )
    ]
    
    for user in demo_users:
        db.add(user)
    db.commit()
    print(f"✅ Created {len(demo_users)} demo users for testing")
    
    # ============================================
    # Create products with real Unsplash images
    # ============================================
    
    products = [
        Product(
            id=str(uuid.uuid4()),
            name="Daura Suruwal Set",
            description="Traditional Nepali formal wear with dhaka topi. Perfect for festivals and special occasions.",
            category="Men",
            sub_category="Traditional",
            gender="Men",
            style=["Formal", "Traditional"],
            tags=["Cotton", "Handmade", "Nepali", "Festival"],
            price=3500,
            discount_price=2800,
            brand="Nepali Handicraft",
            material="Cotton",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=500&fit=crop",
            stock_quantity=20
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Kurta Suruwal",
            description="Elegant kurta with suruwal for women. Handcrafted with traditional Nepali patterns.",
            category="Women",
            sub_category="Traditional",
            gender="Women",
            style=["Traditional", "Casual"],
            tags=["Silk", "Festival", "Nepali", "Elegant"],
            price=2500,
            discount_price=2000,
            brand="Festival Wear",
            material="Silk",
            season=["Dashain", "Tihar"],
            image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&h=500&fit=crop",
            stock_quantity=15
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Casual Denim Jacket",
            description="Modern denim jacket for men. Perfect for casual outings and streetwear style.",
            category="Men",
            sub_category="Jackets",
            gender="Men",
            style=["Casual", "Streetwear"],
            tags=["Denim", "Winter", "Modern", "Street"],
            price=5000,
            discount_price=4200,
            brand="Urban Nepali",
            material="Denim",
            season=["Winter", "Monsoon"],
            image_url="https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=400&h=500&fit=crop",
            stock_quantity=10
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Saree Collection",
            description="Beautiful handwoven saree with traditional patterns. Perfect for weddings and festivals.",
            category="Women",
            sub_category="Saree",
            gender="Women",
            style=["Traditional", "Festival"],
            tags=["Silk", "Handmade", "Colorful", "Wedding"],
            price=5500,
            discount_price=4500,
            brand="Handloom Nepal",
            material="Silk",
            season=["Dashain", "Tihar", "Wedding"],
            image_url="https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=400&h=500&fit=crop",
            stock_quantity=8
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Mountain Trekking Gear",
            description="Durable trekking pants and jacket combo for Himalayan adventures.",
            category="Men",
            sub_category="Outdoor",
            gender="Men",
            style=["Sport", "Adventure"],
            tags=["Trekking", "Outdoor", "Warm", "Himalayan"],
            price=8000,
            discount_price=6500,
            brand="Himalayan Gear",
            material="Polyester",
            season=["Summer", "Winter"],
            image_url="https://images.unsplash.com/photo-1539109136881-3be0616acf4b?w=400&h=500&fit=crop",
            stock_quantity=5
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Kids Festival Dress",
            description="Colorful dress for kids during festivals. Soft and comfortable cotton fabric.",
            category="Kids",
            sub_category="Dresses",
            gender="Kids",
            style=["Casual", "Festival"],
            tags=["Colorful", "Cotton", "Handmade", "Comfort"],
            price=1500,
            discount_price=1200,
            brand="Little Nepal",
            material="Cotton",
            season=["Dashain", "Tihar"],
            image_url="https://images.unsplash.com/photo-1519278409-1f56fdda7fe5?w=400&h=500&fit=crop",
            stock_quantity=25
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Pashmina Shawl",
            description="Luxurious pashmina shawl for winter. Handwoven by skilled Nepali artisans.",
            category="Women",
            sub_category="Accessories",
            gender="Women",
            style=["Traditional", "Winter", "Luxury"],
            tags=["Pashmina", "Warm", "Luxury", "Handmade"],
            price=12000,
            discount_price=10000,
            brand="Himalayan Pashmina",
            material="Pashmina",
            season=["Winter"],
            image_url="https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=400&h=500&fit=crop",
            stock_quantity=12
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Men's Formal Blazer",
            description="Elegant blazer for formal occasions. Perfect for weddings and office wear.",
            category="Men",
            sub_category="Suits",
            gender="Men",
            style=["Formal", "Classic"],
            tags=["Wool", "Office", "Classic", "Wedding"],
            price=7500,
            discount_price=6000,
            brand="Nepali Tailors",
            material="Wool",
            season=["Winter"],
            image_url="https://images.unsplash.com/photo-1591047139829-d91aecb6caea?w=400&h=500&fit=crop",
            stock_quantity=8
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Yoga Wear Set",
            description="Comfortable yoga pants and top for your fitness routine.",
            category="Women",
            sub_category="Activewear",
            gender="Women",
            style=["Sport", "Comfort"],
            tags=["Yoga", "Stretch", "Breathable", "Fitness"],
            price=3500,
            discount_price=2800,
            brand="Nepali Fitness",
            material="Spandex",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1518314916381-77a37c2a49ae?w=400&h=500&fit=crop",
            stock_quantity=15
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Traditional Newari Topi",
            description="Traditional Newari style hat. A symbol of Nepali culture and heritage.",
            category="Men",
            sub_category="Accessories",
            gender="Men",
            style=["Traditional"],
            tags=["Newari", "Handmade", "Unique", "Cultural"],
            price=800,
            discount_price=650,
            brand="Nepali Arts",
            material="Cotton",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=500&fit=crop",
            stock_quantity=30
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Leather Boots",
            description="Durable leather boots for everyday wear. Made with premium Nepali leather.",
            category="Men",
            sub_category="Footwear",
            gender="Men",
            style=["Casual", "Formal"],
            tags=["Leather", "Durable", "Style", "Premium"],
            price=4500,
            discount_price=3800,
            brand="Nepali Leather",
            material="Leather",
            season=["Winter", "Monsoon"],
            image_url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=500&fit=crop",
            stock_quantity=10
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Baby Cotton Set",
            description="Soft cotton set for babies. Gentle on skin and perfect for all seasons.",
            category="Kids",
            sub_category="Baby Wear",
            gender="Kids",
            style=["Comfort", "Casual"],
            tags=["Cotton", "Soft", "Baby", "Comfort"],
            price=1200,
            discount_price=1000,
            brand="Baby Nepal",
            material="Cotton",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1522771930-78848d9293e8?w=400&h=500&fit=crop",
            stock_quantity=40
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Dhaka Topi Collection",
            description="Traditional Nepali dhaka topi. A must-have accessory for Nepali men.",
            category="Men",
            sub_category="Accessories",
            gender="Men",
            style=["Traditional"],
            tags=["Dhaka", "Handmade", "Nepali", "Cultural"],
            price=600,
            discount_price=450,
            brand="Dhaka Handicraft",
            material="Cotton",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1558618666-fcd25c85f4a7?w=400&h=500&fit=crop",
            stock_quantity=50
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Designer Bridal Saree",
            description="Luxury bridal saree with gold embroidery. Make your wedding day unforgettable.",
            category="Women",
            sub_category="Wedding",
            gender="Women",
            style=["Traditional", "Luxury", "Bridal"],
            tags=["Silk", "Gold", "Bridal", "Luxury"],
            price=25000,
            discount_price=22000,
            brand="Nepali Bridal",
            material="Silk",
            season=["Wedding", "Dashain"],
            image_url="https://images.unsplash.com/photo-1583391733956-3750e0ff4e8b?w=400&h=500&fit=crop",
            stock_quantity=3
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Hiking Backpack",
            description="Durable backpack for hiking and outdoor adventures in the Himalayas.",
            category="Men",
            sub_category="Outdoor",
            gender="Men",
            style=["Sport", "Adventure"],
            tags=["Hiking", "Outdoor", "Lightweight", "Durable"],
            price=6000,
            discount_price=5000,
            brand="Himalayan Gear",
            material="Polyester",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400&h=500&fit=crop",
            stock_quantity=8
        ),
        Product(
            id=str(uuid.uuid4()),
            name="Winter Beanie Set",
            description="Warm beanie and scarf set. Stay cozy during cold Nepali winters.",
            category="Women",
            sub_category="Accessories",
            gender="Women",
            style=["Casual", "Winter"],
            tags=["Warm", "Knit", "Comfort", "Winter"],
            price=1500,
            discount_price=1200,
            brand="Nepali Knits",
            material="Wool",
            season=["Winter"],
            image_url="https://images.unsplash.com/photo-1531310197839-ccf54634509e?w=400&h=500&fit=crop",
            stock_quantity=20
        ),
        Product(
            id=str(uuid.uuid4()),
            name="School Uniform Set",
            description="Durable uniform for school kids. Comfortable and long-lasting.",
            category="Kids",
            sub_category="School Wear",
            gender="Kids",
            style=["Formal"],
            tags=["Cotton", "Durable", "Comfort", "School"],
            price=2500,
            discount_price=2200,
            brand="School Nepal",
            material="Cotton",
            season=["All"],
            image_url="https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=400&h=500&fit=crop",
            stock_quantity=35
        )
    ]
    
    for product in products:
        db.add(product)
    db.commit()
    print(f"✅ Created {len(products)} products")
    
    # ============================================
    # Create demo interactions (for testing recommendations)
    # These simulate user behavior so the system has some data
    # ============================================
    
    user_ids = [user.id for user in demo_users]
    product_ids = [product.id for product in products]
    
    interaction_types = ["VIEW", "VIEW", "VIEW", "CLICK", "WISHLIST_ADD", "CART_ADD", "PURCHASE"]
    weights = {
        "VIEW": 0.5,
        "CLICK": 0.75,
        "WISHLIST_ADD": 1.0,
        "CART_ADD": 1.5,
        "PURCHASE": 2.0
    }
    
    interactions_created = 0
    for _ in range(80):
        interaction_type = random.choice(interaction_types)
        interaction = Interaction(
            id=str(uuid.uuid4()),
            user_id=random.choice(user_ids),
            product_id=random.choice(product_ids),
            interaction_type=interaction_type,
            weight=weights.get(interaction_type, 0.5),
            device_type=random.choice(["Mobile", "Desktop", "Tablet"]),
            browser=random.choice(["Chrome", "Firefox", "Safari"]),
            time_spent=random.randint(5, 120)
        )
        db.add(interaction)
        interactions_created += 1
    
    db.commit()
    print(f"✅ Created {interactions_created} demo interactions")
    print("=" * 50)
    print("📝 NOTE: Demo users created for testing:")
    print("   Username: demo_ram, demo_sita, demo_hari")
    print("   Password: demo123")
    print("=" * 50)
    print("✅ Database seeding complete!")
    print("💡 Real users can now register and get personalized recommendations!")