"""
Global Signal Definitions
Centralized signals for cross-module communication
"""
from PyQt6.QtCore import QObject, pyqtSignal


class AppSignals(QObject):
    """Global application signals"""
    
    # Theme signals
    theme_changed = pyqtSignal(str)  # theme_name
    
    # Data signals
    data_updated = pyqtSignal(str)  # model_name
    
    # Navigation signals
    navigate_to = pyqtSignal(str)  # feature_name
    
    # Config signals
    config_reloaded = pyqtSignal()
    
    # Database signals
    database_reset = pyqtSignal()


# Global signals instance
app_signals = AppSignals()
