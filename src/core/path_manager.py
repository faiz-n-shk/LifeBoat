"""
Path Manager
Manages custom paths for config and database files
"""
import json
import shutil
import sys
import os
from pathlib import Path
from src.core.debug import debug_log


def get_resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


class PathManager:
    """Manages custom file paths for config and database"""
    
    def __init__(self):
        # Determine if running as bundled app or in development
        self.is_bundled = getattr(sys, 'frozen', False)
        
        if self.is_bundled:
            # For bundled app, base_dir is the directory containing the executable
            self.base_dir = Path(sys.executable).parent
        else:
            # For development, base_dir is the project root
            self.base_dir = Path(__file__).parent.parent.parent
        
        # For production (bundled), check for portable mode
        if self.is_bundled:
            # Check for portable mode marker file
            portable_marker = self.base_dir / "portable.txt"
            
            if portable_marker.exists():
                # PORTABLE MODE: Store everything in local UserData folder
                self.user_data_dir = self.base_dir / "UserData"
                debug_log('PathManager', f"Portable mode enabled, using: {self.user_data_dir}")
            else:
                # STANDARD MODE: Use AppData/Roaming for user data
                appdata = os.getenv('APPDATA')
                if not appdata:
                    appdata = Path.home() / 'AppData' / 'Roaming'
                self.user_data_dir = Path(appdata) / 'Lifeboat'
                debug_log('PathManager', f"Standard mode, using AppData: {self.user_data_dir}")
            
            # Ensure user data directory exists
            self.user_data_dir.mkdir(exist_ok=True, parents=True)
            
            # Default paths in user data directory
            self.paths_config_file = self.user_data_dir / "custom_paths.json"
            self.default_config = self.user_data_dir / "config.yaml"
            self.default_themes = self.user_data_dir / "themes.yaml"
            self.default_db = self.user_data_dir / "lifeboat.db"
            self.default_logs = self.user_data_dir / "logs"
            
        else:
            # Development: Use project directory
            self.user_data_dir = self.base_dir
            self.paths_config_file = self.base_dir / "data" / "custom_paths.json"
            self.default_config = self.base_dir / "config" / "config.yaml"
            self.default_themes = self.base_dir / "config" / "themes.yaml"
            self.default_db = self.base_dir / "data" / "lifeboat.db"
            self.default_logs = self.base_dir / "logs"
            
            debug_log('PathManager', f"Development mode, using: {self.base_dir}")
            
            # Ensure directories exist (development only)
            (self.base_dir / "config").mkdir(exist_ok=True, parents=True)
            (self.base_dir / "data").mkdir(exist_ok=True, parents=True)
            (self.base_dir / "logs").mkdir(exist_ok=True, parents=True)
        
        # Ensure logs directory exists
        self.default_logs.mkdir(exist_ok=True, parents=True)
        
        # User fonts directory (always writable, relative to user data)
        if self.is_bundled:
            self.user_fonts_dir = self.user_data_dir / "fonts"
        else:
            self.user_fonts_dir = self.base_dir / "assets" / "fonts"
        self.user_fonts_dir.mkdir(exist_ok=True, parents=True)
        
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
            debug_log('PathManager.get_database_path', f"Using custom: {path}")
            return path
        debug_log('PathManager.get_database_path', f"Using default: {self.default_db}")
        return self.default_db
    
    def get_themes_path(self):
        """Get the active themes file path"""
        custom_path = self.custom_paths.get('themes_path')
        if custom_path:
            path = Path(custom_path)
            debug_log('PathManager.get_themes_path', f"Using custom: {path}")
            return path
        debug_log('PathManager.get_themes_path', f"Using default: {self.default_themes}")
        return self.default_themes
    
    def get_logs_path(self):
        """Get the active logs directory path"""
        custom_path = self.custom_paths.get('logs_path')
        if custom_path:
            path = Path(custom_path)
            debug_log('PathManager.get_logs_path', f"Using custom: {path}")
            return path
        debug_log('PathManager.get_logs_path', f"Using default: {self.default_logs}")
        return self.default_logs
    
    def get_user_fonts_dir(self):
        """Get the user fonts directory (writable location for imported fonts)"""
        return self.user_fonts_dir
    
    def set_custom_config_path(self, directory):
        """
        Set custom directory for config file
        Does NOT copy if file already exists at custom location
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_config = directory / "config.yaml"
            
            # Only create/copy config if it doesn't exist in custom location
            # This prevents overwriting existing custom configs
            if not custom_config.exists():
                # Check if default config exists to copy from
                if self.default_config.exists():
                    shutil.copy2(self.default_config, custom_config)
                    debug_log('PathManager', f"Copied default config to: {custom_config}")
                else:
                    # Create config.yaml with minimal default content
                    # Import config_template to get default structure
                    from src.core.config_template import DEFAULT_CONFIG
                    import yaml
                    with open(custom_config, 'w', encoding='utf-8') as f:
                        yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
                    debug_log('PathManager', f"Created default config at: {custom_config}")
            else:
                debug_log('PathManager', f"Using existing config at: {custom_config}")
            
            self.custom_paths['config_path'] = str(custom_config)
            self._save_custom_paths()
            
            # Reload config from the new custom location
            from src.core.config import config
            debug_log('PathManager', f"Reloading config from custom location: {custom_config}")
            config.reload()
            
            return True, f"Config file set to: {custom_config}"
        except Exception as e:
            return False, f"Error setting custom config path: {e}"
    
    def set_custom_database_path(self, directory):
        """
        Set custom directory for database file
        Does NOT copy if file already exists at custom location
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_db = directory / "lifeboat.db"
            
            # Only create/copy database if it doesn't exist in custom location
            if not custom_db.exists():
                # Check if default database exists to copy from
                if self.default_db.exists():
                    shutil.copy2(self.default_db, custom_db)
                    debug_log('PathManager', f"Copied default database to: {custom_db}")
                else:
                    # Create new database using database module
                    from src.core.database import Database
                    db = Database(str(custom_db))
                    db.initialize_database()
                    debug_log('PathManager', f"Created new database at: {custom_db}")
            else:
                debug_log('PathManager', f"Using existing database at: {custom_db}")
            
            self.custom_paths['database_path'] = str(custom_db)
            self._save_custom_paths()
            
            return True, f"Database file set to: {custom_db}"
        except Exception as e:
            return False, f"Error setting custom database path: {e}"
    
    def set_custom_themes_path(self, directory):
        """
        Set custom directory for themes file
        Does NOT copy if file already exists at custom location
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            custom_themes = directory / "themes.yaml"
            
            # Only create/copy themes if it doesn't exist in custom location
            if not custom_themes.exists():
                # Check if default themes exists to copy from
                if self.default_themes.exists():
                    shutil.copy2(self.default_themes, custom_themes)
                    debug_log('PathManager', f"Copied default themes to: {custom_themes}")
                else:
                    # Create themes.yaml with default content
                    default_content = "custom_themes: []\n"
                    with open(custom_themes, 'w', encoding='utf-8') as f:
                        f.write(default_content)
                    debug_log('PathManager', f"Created default themes at: {custom_themes}")
            else:
                debug_log('PathManager', f"Using existing themes at: {custom_themes}")
            
            self.custom_paths['themes_path'] = str(custom_themes)
            self._save_custom_paths()
            
            return True, f"Themes file set to: {custom_themes}"
        except Exception as e:
            return False, f"Error setting custom themes path: {e}"
    
    def set_custom_logs_path(self, directory):
        """
        Set custom directory for logs
        Only copies logs that don't already exist at custom location
        """
        try:
            directory = Path(directory)
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
            
            # Only copy logs that don't exist in custom location
            if self.default_logs.exists():
                for log_file in self.default_logs.glob("*.log"):
                    dest = directory / log_file.name
                    if not dest.exists():
                        shutil.copy2(log_file, dest)
                        debug_log('PathManager', f"Copied log file to: {dest}")
                    else:
                        debug_log('PathManager', f"Log file already exists at: {dest}")
            
            self.custom_paths['logs_path'] = str(directory)
            self._save_custom_paths()
            
            return True, f"Logs directory set to: {directory}"
        except Exception as e:
            return False, f"Error setting custom logs path: {e}"
    
    def reset_config_to_default(self):
        """Reset config to default location"""
        if 'config_path' in self.custom_paths:
            del self.custom_paths['config_path']
            self._save_custom_paths()
            
            # Force reload config from default location
            from src.core.config import config
            print("[PathManager] Reloading config from default location after reset")
            config.reload()
            
        return True, "Config reset to default location"
    
    def reset_database_to_default(self):
        """Reset database to default location"""
        debug_log('PathManager.reset_database_to_default', f"Current custom paths: {self.custom_paths}")
        if 'database_path' in self.custom_paths:
            del self.custom_paths['database_path']
            self._save_custom_paths()
            print("[PathManager.reset_database_to_default] Database path reset to default")
        return True, "Database reset to default location"
    
    def reset_themes_to_default(self):
        """Reset themes to default location"""
        debug_log('PathManager.reset_themes_to_default', f"Current custom paths: {self.custom_paths}")
        if 'themes_path' in self.custom_paths:
            del self.custom_paths['themes_path']
            self._save_custom_paths()
            print("[PathManager.reset_themes_to_default] Themes path reset to default")
        return True, "Themes reset to default location"
    
    def reset_logs_to_default(self):
        """Reset logs to default location"""
        debug_log('PathManager.reset_logs_to_default', f"Current custom paths: {self.custom_paths}")
        if 'logs_path' in self.custom_paths:
            del self.custom_paths['logs_path']
            self._save_custom_paths()
            print("[PathManager.reset_logs_to_default] Logs path reset to default")
        return True, "Logs reset to default location"
    
    def restore_default_config(self):
        """
        Restore config from default template
        Recreates config.yaml with default values
        """
        try:
            from src.core.config_template import create_default_config
            
            # Get the current config path (could be custom or default)
            current_config = self.get_config_path()
            print(f"Restoring config at: {current_config}")
            print(f"Custom paths: {self.custom_paths}")
            
            # Create backup first if file exists
            if current_config.exists():
                backup_path = current_config.with_suffix('.yaml.backup')
                import shutil
                shutil.copy2(current_config, backup_path)
                print(f"Backup created at: {backup_path}")
                
                # Delete the config
                current_config.unlink()
                print(f"Deleted config at: {current_config}")
            else:
                print(f"Config file doesn't exist at: {current_config}")
            
            # Ensure the directory exists
            current_config.parent.mkdir(parents=True, exist_ok=True)
            
            # Create fresh config from template
            success = create_default_config(current_config)
            print(f"Create default config result: {success}")
            
            if success:
                # Verify the file was created
                if current_config.exists():
                    print(f"Config file created successfully at: {current_config}")
                    
                    # Force reload the config in memory
                    from src.core.config import config
                    config.reload()
                    print("Config reloaded from file")
                    
                    return True, f"Config restored to default settings at:\n{current_config}\n\nA backup was created. Please restart the app to see all changes."
                else:
                    print(f"ERROR: Config file was not created at: {current_config}")
                    return False, f"Config file was not created at: {current_config}"
            else:
                return False, "Failed to create default config file"
                
        except Exception as e:
            print(f"Error in restore_default_config: {e}")
            import traceback
            traceback.print_exc()
            return False, f"Error restoring config: {e}"
    
    def restore_default_database(self):
        """
        Restore database from default template
        Creates a fresh database with default structure
        """
        try:
            from src.core.database import db, initialize_database
            
            current_db = self.get_database_path()
            
            debug_log('PathManager.restore_default_database', f"Current DB: {current_db}")
            
            # CRITICAL: Close database connection before deleting
            try:
                if not db.is_closed():
                    db.close()
                    print("[PathManager.restore_default_database] Database connection closed")
            except Exception as e:
                debug_log('PathManager.restore_default_database', f"Warning closing DB: {e}")
            
            # Backup current database
            if current_db.exists():
                backup = current_db.with_suffix('.db.backup')
                shutil.copy2(current_db, backup)
                current_db.unlink()
                debug_log('PathManager.restore_default_database', f"Backup saved to: {backup}")
            
            # Recreate fresh database with default settings
            print("[PathManager.restore_default_database] Creating fresh database...")
            initialize_database()
            print("[PathManager.restore_default_database] Fresh database created with defaults")
            
            return True, "Database restored to default settings. Please restart the app to complete."
        except Exception as e:
            debug_log('PathManager.restore_default_database', f"ERROR: {e}")
            import traceback
            traceback.print_exc()
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
            },
            'logs': {
                'current': str(self.get_logs_path()),
                'default': str(self.default_logs),
                'is_custom': 'logs_path' in self.custom_paths
            }
        }


# Global instance
path_manager = PathManager()
