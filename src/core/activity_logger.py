"""
Activity Logger
Logs user activities across the application
"""
import os
from datetime import datetime
from pathlib import Path
from src.core.path_manager import path_manager


class ActivityLogger:
    """Singleton activity logger"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.current_date = datetime.now().date()
        self.log_file = None
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure log file exists and rotate if needed"""
        logs_dir = path_manager.get_logs_path()
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        today = datetime.now().date()
        
        # Check if we need to rotate log
        if self.current_date != today and self.log_file:
            self._rotate_log()
            self.current_date = today
        
        self.log_file = logs_dir / "latest.log"
    
    def _rotate_log(self):
        """Rotate current log file"""
        if not self.log_file or not self.log_file.exists():
            return
        
        logs_dir = path_manager.get_logs_path()
        old_log_name = f"{self.current_date.strftime('%Y-%m-%d')}_log.log"
        old_log_path = logs_dir / old_log_name
        
        try:
            self.log_file.rename(old_log_path)
        except Exception as e:
            print(f"Error rotating log: {e}")
    
    def log(self, feature: str, action: str, details: str = None):
        """
        Log an activity
        
        Args:
            feature: Feature name (Tasks, Todos, Calendar, etc.)
            action: Action performed (created, updated, deleted, completed, etc.)
            details: Additional details about the action
        """
        try:
            self._ensure_log_file()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] [{feature}] {action}"
            
            if details:
                log_entry += f" - {details}"
            
            log_entry += "\n"
            
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        
        except Exception as e:
            print(f"Error writing to log: {e}")
    
    def get_recent_activities(self, limit: int = 10, exclude_features: list = None):
        """
        Get recent activities from log
        
        Args:
            limit: Maximum number of activities to return
            exclude_features: List of features to exclude (e.g., ['Settings'])
        
        Returns:
            List of activity dictionaries
        """
        try:
            self._ensure_log_file()
            
            if not self.log_file.exists():
                return []
            
            activities = []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Read from end to get most recent first
            for line in reversed(lines):
                if len(activities) >= limit:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # Parse log entry: [timestamp] [feature] action - details
                try:
                    parts = line.split('] ', 2)
                    if len(parts) < 3:
                        continue
                    
                    timestamp_str = parts[0].replace('[', '')
                    feature = parts[1].replace('[', '')
                    action_details = parts[2]
                    
                    # Skip excluded features
                    if exclude_features and feature in exclude_features:
                        continue
                    
                    # Split action and details
                    if ' - ' in action_details:
                        action, details = action_details.split(' - ', 1)
                    else:
                        action = action_details
                        details = None
                    
                    timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                    
                    activities.append({
                        'timestamp': timestamp,
                        'feature': feature,
                        'action': action,
                        'details': details
                    })
                
                except Exception as e:
                    print(f"Error parsing log line: {e}")
                    continue
            
            return activities
        
        except Exception as e:
            print(f"Error reading activities: {e}")
            return []


# Global logger instance
activity_logger = ActivityLogger()
