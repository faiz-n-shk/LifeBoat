"""
Create default database template
This script creates a clean database template with default structure
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import db, initialize_database
from src.core import config
import shutil

def create_default_template():
    """Create a default database template"""
    template_path = Path(__file__).parent.parent / "data" / "default_settings.db"
    temp_db_path = Path(__file__).parent.parent / "data" / "temp_template.db"
    
    # Backup existing database if it exists
    if config.DATABASE_PATH.exists():
        backup_path = config.DATABASE_PATH.with_suffix('.db.backup_before_template')
        shutil.copy2(config.DATABASE_PATH, backup_path)
        print(f"Backed up existing database to: {backup_path}")
    
    # Temporarily point to temp database
    original_db = config.DATABASE_PATH
    
    try:
        # Create fresh database
        if temp_db_path.exists():
            temp_db_path.unlink()
        
        # Initialize database with default structure
        db.init(str(temp_db_path))
        initialize_database()
        db.close()
        
        # Copy to template location
        shutil.copy2(temp_db_path, template_path)
        print(f"✓ Default database template created: {template_path}")
        
        # Clean up temp file
        if temp_db_path.exists():
            temp_db_path.unlink()
        
        print("\nTemplate database created successfully!")
        print("This template will be used when users restore database to defaults.")
        
    except Exception as e:
        print(f"Error creating template: {e}")
        if temp_db_path.exists():
            temp_db_path.unlink()

if __name__ == "__main__":
    create_default_template()
