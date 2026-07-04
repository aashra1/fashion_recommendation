# check_users.py
from app.database import SessionLocal
from app.models import User

def check_users():
    db = SessionLocal()
    users = db.query(User).all()
    
    print("="*50)
    print("📊 Registered Users in Database")
    print("="*50)
    
    if not users:
        print("❌ No users found in database!")
        print("Please register first.")
    else:
        for user in users:
            print(f"\n👤 Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Registered: {user.created_at}")
            print("-"*30)
    
    db.close()

if __name__ == "__main__":
    check_users()