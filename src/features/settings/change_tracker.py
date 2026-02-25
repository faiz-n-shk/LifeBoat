"""
Settings Change Tracker
Tracks changes made in settings before they're applied
"""
from typing import Dict, List, Tuple


class SettingsChangeTracker:
    """Tracks pending changes in settings"""
    
    def __init__(self):
        self.changes: Dict[str, Tuple[any, any]] = {}  # key: (old_value, new_value)
        self.requires_restart = False
    
    def track_change(self, key: str, old_value: any, new_value: any, needs_restart: bool = False):
        """Track a setting change"""
        if old_value != new_value:
            self.changes[key] = (old_value, new_value)
            if needs_restart:
                self.requires_restart = True
    
    def has_changes(self) -> bool:
        """Check if there are pending changes"""
        return len(self.changes) > 0
    
    def get_changes_summary(self) -> List[str]:
        """Get a list of change descriptions"""
        summary = []
        for key, (old_val, new_val) in self.changes.items():
            # Format key nicely
            display_key = key.replace('_', ' ').replace('.', ' > ').title()
            summary.append(f"{display_key}: {old_val} → {new_val}")
        return summary
    
    def clear(self):
        """Clear all tracked changes"""
        self.changes.clear()
        self.requires_restart = False
    
    def needs_restart(self) -> bool:
        """Check if changes require app restart"""
        return self.requires_restart


# Global change tracker instance
change_tracker = SettingsChangeTracker()
