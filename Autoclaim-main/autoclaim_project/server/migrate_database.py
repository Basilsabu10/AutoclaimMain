"""
Database Migration Script - Recreate Database with New Schema
For SQLite Development Environment

This script will:
1. Backup existing database
2. Delete old database
3. Create new database with comprehensive forensic analysis fields
"""

import os
import shutil
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "autoclaim.db"
BACKUP_DIR = BASE_DIR / "db_backups"

def migrate_database():
    """Migrate database to v2.0 with comprehensive forensic fields"""
    
    print("=" * 80)
    print("DATABASE MIGRATION - Comprehensive Forensic Analysis v2.0")
    print("=" * 80)
    
    # Create backup directory
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Step 1: Backup existing database
    if DB_PATH.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"autoclaim_backup_{timestamp}.db"
        shutil.copy2(DB_PATH, backup_path)
        print(f"\n✅ Backed up existing database to: {backup_path}")
    else:
        print("\n⚠️  No existing database found")
    
    # Step 2: Delete old database
    if DB_PATH.exists():
        DB_PATH.unlink()
        print(f"✅ Deleted old database: {DB_PATH}")
    
    # Step 3: Create new database with updated schema
    print("\n🔄 Creating new database with comprehensive schema...")
    print("   (Database will be auto-created on next server start)")
    
    # Import models to trigger database creation
    try:
        from app.db.database import Base, engine
        from app.db import models
        
        # Create all tables with new schema
        Base.metadata.create_all(bind=engine)
        print("\n✅ New database created successfully!")
        
        # Display new ForensicAnalysis fields
        print("\n📊 New ForensicAnalysis Table Fields:")
        print("   - YOLOv8 Detection (4 fields)")
        print("   - Forensic Analysis / Image Integrity (4 fields)")
        print("   - Vehicle Identification (11 fields)")
        print("   - Enhanced Damage Assessment (8 fields)")
        print("   - Pre-existing Damage Detection (4 fields)")
        print("   - Contextual Analysis (5 fields)")
        print("   - Cross-verification (4 fields)")
        print("   - Risk Assessment & Final Assessment (7 fields)")
        print("   - Total: 60+ comprehensive forensic fields")
        
        print("\n" + "=" * 80)
        print("MIGRATION COMPLETE!")
        print("=" * 80)
        print("\n📝 Next Steps:")
        print("   1. Restart the server (if running)")
        print("   2. Submit a new claim to test comprehensive forensic analysis")
        print("   3. Run: python test_ai_storage.py")
        print("\n⚠️  Note: All old claims data has been backed up but not migrated.")
        print("   Old data is in: " + str(backup_path if DB_PATH.exists() else "No backup needed"))
        
    except Exception as e:
        print(f"\n❌ Error creating database: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    migrate_database()
