"""
Path Manager
Manages custom paths for config and database files
"""
import json
import shutil
from pathlib import Path


class PathManager:
    """Manages custom file paths for config and database"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.paths_config_file = self.base_dir / "data" / "custom_paths.json"
        self.default_config = self.base_dir / "config" / "config.yaml"
        self.default_themes = self.base_dir / "config" / "themes.yaml"
        self.default_db = self.base_dir / "data" / "lifeboat.db"
        self.default_db_template = self.base_dir / "data" / "default_settings.db"
        
        # Ensure directories exist
        (self.base_dir / "config").mkdir(exist_ok=True, parents=True)
        (self.base_dir / "data").mkdir(exist_ok=True, parents=True)
        
        # Load custom paths
        self.custom_paths = self._load_custom_paths()
    
    def _load_custom_paths(self):
        """Load custom paths from config file"""
        if self.paths_config_file.exists():
            try:
                with open(self.paths_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading custom paths: {e}")
                return {}
        return {}
    
    def _save_custom_paths(self):
        """Save custom paths to config file"""
        try:
            with open(self.paths_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_paths, f, indent=2)
        except Exception as e:
            print(f"Error saving custom paths: {e}")
    
    def get_config_path(self):
        """Get the active config file path"""
        custom_path = self.custom_paths.get('config_path')
        if custom_path:
            path = Path(custom_path)
            if path.exists():
                return path
        return self.default_config
    
    def get_database_path(self):
        """Get the active database file path"""
        custom_path = self.custom_paths.get('database_path')
        if custom_path:
            path = Path(custom_path)
            if path.exists():
                return path
        return self.default_db
    
    def get_themes_path(self):
        """Get the active themes file path"""
        custom_path = self.custom_paths.get('themes_path')
        if custom_path:
            path = Path(custom_path)
            if path.exists():
                return path
        return self.default_themes
    
    def set_custom_config_path(self, directory):
        """
        Set custom directory for config file
        Copies config to new location if it doesn't exist
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_config = directory / "config.yaml"
            
            # Copy config if it doesn't exist in custom location
            if not custom_config.exists():
                shutil.copy2(self.default_config, custom_config)
            
            self.custom_paths['config_path'] = str(custom_config)
            self._save_custom_paths()
            
            return True, f"Config file set to: {custom_config}"
        except Exception as e:
            return False, f"Error setting custom config path: {e}"
    
    def set_custom_database_path(self, directory):
        """
        Set custom directory for database file
        Copies database to new location if it doesn't exist
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_db = directory / "lifeboat.db"
            
            # Copy database if it doesn't exist in custom location
            if not custom_db.exists() and self.default_db.exists():
                shutil.copy2(self.default_db, custom_db)
            
            self.custom_paths['database_path'] = str(custom_db)
            self._save_custom_paths()
            
            return True, f"Database file set to: {custom_db}"
        except Exception as e:
            return False, f"Error setting custom database path: {e}"
    
    def set_custom_themes_path(self, directory):
        """
        Set custom directory for themes file
        Copies themes to new location if it doesn't exist
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_themes = directory / "themes.yaml"
            
            # Copy themes if it doesn't exist in custom location
            if not custom_themes.exists():
                shutil.copy2(self.default_themes, custom_themes)
            
            self.custom_paths['themes_path'] = str(custom_themes)
            self._save_custom_paths()
            
            return True, f"Themes file set to: {custom_themes}"
        except Exception as e:
            return False, f"Error setting custom themes path: {e}"
    
    def reset_config_to_default(self):
        """Reset config to default location"""
        if 'config_path' in self.custom_paths:
            del self.custom_paths['config_path']
            self._save_custom_paths()
        return True, "Config reset to default location"
    
    def reset_database_to_default(self):
        """Reset database to default location"""
        if 'database_path' in self.custom_paths:
            del self.custom_paths['database_path']
            self._save_custom_paths()
        return True, "Database reset to default location"
    
    def reset_themes_to_default(self):
        """Reset themes to default location"""
        if 'themes_path' in self.custom_paths:
            del self.custom_paths['themes_path']
            self._save_custom_paths()
        return True, "Themes reset to default location"
    
    def restore_default_config(self):
        """
        Restore config from default template
        Recreates config.yaml with default values
        """
        try:
            from src.core.config_template import create_default_config
            current_config = self.get_config_path()
            
            # Delete existing config
            if current_config.exists():
                current_config.unlink()
            
            # Create fresh config from template
            create_default_config(current_config)
            return True, "Config restored to default settings. Please restart the app."
        except Exception as e:
            return False, f"Error restoring config: {e}"
    
    def restore_default_database(self):
        """
        Restore database from default template
        Creates a fresh database with default structure
        """
        try:
            current_db = self.get_database_path()
            template_path = current_db.parent / "default_settings.db"
            
            # Backup current database
            if current_db.exists():
                backup = current_db.with_suffix('.db.backup')
                shutil.copy2(current_db, backup)
                current_db.unlink()
                print(f"Backup saved to: {backup}")
            
            # Delete old template if exists (might have outdated schema)
            if template_path.exists():
                template_path.unlink()
                print("Removed old template")
            
            # Database will be recreated with current schema on next app start
            return True, "Database reset. Please restart the app to complete."
        except Exception as e:
            return False, f"Error restoring database: {e}"
    
    def get_current_paths_info(self):
        """Get information about current paths"""
        return {
            'config': {
                'current': str(self.get_config_path()),
                'default': str(self.default_config),
                'is_custom': 'config_path' in self.custom_paths
            },
            'themes': {
                'current': str(self.get_themes_path()),
                'default': str(self.default_themes),
                'is_custom': 'themes_path' in self.custom_paths
            },
            'database': {
                'current': str(self.get_database_path()),
                'default': str(self.default_db),
                'is_custom': 'database_path' in self.custom_paths
            }
        }


# Global instance
path_manager = PathManager()
