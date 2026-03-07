"""
Activity Logger
Logs user activities across the application with session-based log rotation
"""
import os
from datetime import datetime, timedelta
from pathlib import Path
from src.core.path_manager import path_manager
from src.core.debug import debug_log


class ActivityLogger:
    """Singleton activity logger with session-based rotation"""
    
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
        self.session_start = datetime.now()
        self.log_file = None
        self._rotate_on_start()
        self._ensure_log_file()
    
    def _rotate_on_start(self):
        """Rotate log on app start - archive previous latest.log"""
        logs_dir = path_manager.get_logs_path()
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        latest_log = logs_dir / "latest.log"
        
        # If latest.log exists, archive it with timestamp
        if latest_log.exists():
            try:
                # Get file modification time for accurate archiving
                mod_time = datetime.fromtimestamp(latest_log.stat().st_mtime)
                archive_name = f"{mod_time.strftime('%Y-%m-%d_%H-%M-%S')}.log"
                archive_path = logs_dir / archive_name
                
                # Rename to archived log
                latest_log.rename(archive_path)
                debug_log('ActivityLogger', f"Archived previous log to: {archive_name}")
            except Exception as e:
                debug_log('ActivityLogger', f"Error archiving log: {e}")
    
    def _ensure_log_file(self):
        """Ensure log file exists"""
        logs_dir = path_manager.get_logs_path()
        logs_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = logs_dir / "latest.log"
        
        # Log session start
        if not self.log_file.exists():
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write(f"[{self.session_start.strftime('%Y-%m-%d %H:%M:%S')}] [System] App started\n")
    
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
            debug_log('ActivityLogger', f"Error writing to log: {e}")
    
    def get_recent_activities(self, mode: str = "standard", limit: int = 10, exclude_features: list = None):
        """
        Get recent activities from logs
        
        Args:
            mode: "session", "today", "3days", "standard" (7 days), "30days", "all", or "none"
            limit: Maximum number of activities to return
            exclude_features: List of features to exclude (e.g., ['Settings', 'System'])
        
        Returns:
            List of activity dictionaries
        """
        try:
            logs_dir = path_manager.get_logs_path()
            
            if not logs_dir.exists():
                return []
            
            # Determine time filter
            now = datetime.now()
            if mode == "session":
                # Only show activities from current session (latest.log)
                cutoff_time = self.session_start
            elif mode == "today":
                cutoff_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif mode == "3days":
                cutoff_time = now - timedelta(days=3)
            elif mode == "standard":
                cutoff_time = now - timedelta(days=7)
            elif mode == "30days":
                cutoff_time = now - timedelta(days=30)
            elif mode == "all":
                cutoff_time = None
            else:  # "none" or unknown
                return []
            
            activities = []
            
            # Get all log files sorted by modification time (newest first)
            log_files = sorted(
                [f for f in logs_dir.glob("*.log")],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # For session mode, only read latest.log
            if mode == "session":
                log_files = [f for f in log_files if f.name == "latest.log"]
            
            # Read logs from newest to oldest
            for log_file in log_files:
                if len(activities) >= limit:
                    break
                
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
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
                            
                            # Parse timestamp
                            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            
                            # Apply time filter
                            if cutoff_time and timestamp < cutoff_time:
                                continue
                            
                            # Skip excluded features
                            if exclude_features and feature in exclude_features:
                                continue
                            
                            # Split action and details
                            if ' - ' in action_details:
                                action, details = action_details.split(' - ', 1)
                            else:
                                action = action_details
                                details = None
                            
                            activities.append({
                                'timestamp': timestamp,
                                'feature': feature,
                                'action': action,
                                'details': details
                            })
                        
                        except Exception as e:
                            # Skip malformed lines
                            continue
                
                except Exception as e:
                    debug_log('ActivityLogger', f"Error reading log file {log_file.name}: {e}")
                    continue
            
            return activities
        
        except Exception as e:
            debug_log('ActivityLogger', f"Error reading activities: {e}")
            return []


# Global logger instance
activity_logger = ActivityLogger()
