
from database import SessionLocal
from models import User
import auth

# Admin credentials - change these as needed
ADMIN_EMAIL = "admin@autoclaim.com"
ADMIN_PASSWORD = "admin123"  # Change this to a secure password!

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin already exists
        existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if existing:
            print(f"Admin user '{ADMIN_EMAIL}' already exists.")
            return
        
        # Hash the password using the auth module
        hashed_password = auth.get_password_hash(ADMIN_PASSWORD)
        
        # Create admin user
        admin = User(
            email=ADMIN_EMAIL,
            password_hash=hashed_password,
            role="admin"
        )
        db.add(admin)
        db.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: {ADMIN_EMAIL}")
        print(f"Password: {ADMIN_PASSWORD}")
        print(f"Role: admin")
        
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
