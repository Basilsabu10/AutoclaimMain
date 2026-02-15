"""
Database migration script to add new user fields.
Adds name, policy_id, and vehicle_number columns to the users table.
"""

import sqlite3
import os

# Get database path
DB_PATH = os.path.join(os.path.dirname(__file__), "autoclaim.db")

def migrate_database():
    """Add new columns to users table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add name column if it doesn't exist
        if 'name' not in columns:
            print("Adding 'name' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
            print("✓ Added 'name' column")
        else:
            print("✓ 'name' column already exists")
        
        # Add policy_id column if it doesn't exist
        if 'policy_id' not in columns:
            print("Adding 'policy_id' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN policy_id TEXT")
            print("✓ Added 'policy_id' column")
        else:
            print("✓ 'policy_id' column already exists")
        
        # Add vehicle_number column if it doesn't exist
        if 'vehicle_number' not in columns:
            print("Adding 'vehicle_number' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN vehicle_number TEXT")
            print("✓ Added 'vehicle_number' column")
        else:
            print("✓ 'vehicle_number' column already exists")
        
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Database Migration: Adding User Fields")
    print("=" * 50)
    print(f"Database: {DB_PATH}\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        print("Please ensure the database exists before running this migration.")
        exit(1)
    
    migrate_database()
