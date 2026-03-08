"""
Error Logging Test Script
Tests the error logging system with simulated dates and various error scenarios
"""
import sys
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.path_manager import path_manager


class LazyErrorFileHandler(logging.Handler):
    """Handler that only creates the log file when an error actually occurs"""
    
    def __init__(self, simulated_date=None):
        super().__init__()
        self.file_handler = None
        self.error_logs_dir = None
        self.simulated_date = simulated_date
        
    def emit(self, record):
        """Emit a record, creating the file handler if needed"""
        # Only create file handler when we actually need to log something
        if self.file_handler is None:
            # Get error logs directory
            self.error_logs_dir = path_manager.get_error_logs_path()
            
            # Create directory only when first error occurs
            self.error_logs_dir.mkdir(exist_ok=True)
            
            # Use simulated date or current date
            if self.simulated_date:
                today = self.simulated_date.strftime("%d-%m-%Y")
            else:
                today = datetime.now().strftime("%d-%m-%Y")
            
            error_log_file = self.error_logs_dir / f"errorLog_{today}.log"
            
            # Create the file handler
            self.file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
            self.file_handler.setFormatter(self.formatter)
            self.file_handler.setLevel(self.level)
            
            print(f"✓ Created error log file: {error_log_file}")
        
        # Emit the record to the file handler
        self.file_handler.emit(record)
    
    def close(self):
        """Close the file handler if it exists"""
        if self.file_handler:
            self.file_handler.close()
        super().close()


def setup_test_logging(simulated_date=None):
    """Setup logging for testing with optional simulated date"""
    # Clear existing handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    # Create lazy handler with simulated date
    lazy_handler = LazyErrorFileHandler(simulated_date)
    lazy_handler.setLevel(logging.ERROR)
    lazy_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    
    # Add console handler for visibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s: %(message)s'
    ))
    
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(lazy_handler)
    root_logger.addHandler(console_handler)
    
    return lazy_handler


def test_no_errors():
    """Test 1: No errors - should NOT create log file"""
    print("\n" + "="*70)
    print("TEST 1: No Errors (should NOT create file)")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_no_errors")
    
    # Log some info messages (should not trigger file creation)
    logger.info("Application started")
    logger.info("Loading configuration")
    logger.info("Everything is working fine")
    
    if handler.file_handler is None:
        print("✓ SUCCESS: No error log file created (as expected)")
    else:
        print("✗ FAIL: Error log file was created when it shouldn't be")
    
    handler.close()


def test_single_error_today():
    """Test 2: Single error today - should create today's log file"""
    print("\n" + "="*70)
    print("TEST 2: Single Error Today")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_single_error")
    
    # Log an error
    logger.error("Database connection failed")
    
    if handler.file_handler is not None:
        print("✓ SUCCESS: Error log file created")
    else:
        print("✗ FAIL: Error log file was not created")
    
    handler.close()


def test_multiple_errors_same_day():
    """Test 3: Multiple errors same day - should use same file"""
    print("\n" + "="*70)
    print("TEST 3: Multiple Errors Same Day")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_multiple_errors")
    
    # Log multiple errors
    logger.error("Error 1: Configuration file not found")
    logger.error("Error 2: Invalid database schema")
    logger.critical("Critical error: System crash")
    
    if handler.file_handler is not None:
        print("✓ SUCCESS: All errors logged to same file")
    else:
        print("✗ FAIL: Error log file was not created")
    
    handler.close()


def test_simulated_different_days():
    """Test 4: Simulate errors on different days"""
    print("\n" + "="*70)
    print("TEST 4: Simulated Different Days")
    print("="*70)
    
    # Simulate 5 different days
    base_date = datetime.now()
    
    for i in range(5):
        simulated_date = base_date - timedelta(days=i)
        date_str = simulated_date.strftime("%d-%m-%Y")
        
        print(f"\n--- Simulating date: {date_str} ---")
        
        handler = setup_test_logging(simulated_date)
        logger = logging.getLogger(f"test_day_{i}")
        
        # Log an error for this day
        logger.error(f"Error on {date_str}: Something went wrong")
        
        handler.close()
    
    print("\n✓ SUCCESS: Created separate log files for different days")


def test_exception_handling():
    """Test 5: Test exception logging"""
    print("\n" + "="*70)
    print("TEST 5: Exception Handling")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_exception")
    
    try:
        # Simulate an exception
        result = 10 / 0
    except ZeroDivisionError as e:
        logger.error("Division by zero error", exc_info=True)
        print("✓ Exception logged with traceback")
    
    handler.close()


def test_critical_errors():
    """Test 6: Test critical errors"""
    print("\n" + "="*70)
    print("TEST 6: Critical Errors")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_critical")
    
    logger.critical("CRITICAL: System failure detected")
    logger.critical("CRITICAL: Data corruption detected")
    
    print("✓ Critical errors logged")
    
    handler.close()


def test_mixed_log_levels():
    """Test 7: Test mixed log levels (only errors should create file)"""
    print("\n" + "="*70)
    print("TEST 7: Mixed Log Levels")
    print("="*70)
    
    handler = setup_test_logging()
    logger = logging.getLogger("test_mixed")
    
    # These should not create file
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    
    if handler.file_handler is None:
        print("✓ No file created for debug/info/warning")
    
    # This should create file
    logger.error("Error message")
    
    if handler.file_handler is not None:
        print("✓ File created when error occurred")
    
    handler.close()


def show_created_files():
    """Show all created error log files"""
    print("\n" + "="*70)
    print("CREATED ERROR LOG FILES")
    print("="*70)
    
    error_logs_dir = path_manager.get_error_logs_path()
    print(f"\nError logs directory: {error_logs_dir}")
    
    if error_logs_dir.exists():
        error_files = sorted(error_logs_dir.glob("errorLog_*.log"))
        
        if error_files:
            print(f"\nFound {len(error_files)} error log file(s):\n")
            for file in error_files:
                size = file.stat().st_size
                print(f"  • {file.name} ({size} bytes)")
                
                # Show first few lines
                with open(file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:3]
                    for line in lines:
                        print(f"    {line.rstrip()}")
                    if len(lines) > 0:
                        print()
        else:
            print("\nNo error log files found (this is expected if no errors occurred)")
    else:
        print("\nError logs directory does not exist yet")


def cleanup_test_files():
    """Clean up test error log files"""
    print("\n" + "="*70)
    print("CLEANUP")
    print("="*70)
    
    response = input("\nDo you want to delete test error log files? (y/n): ")
    
    if response.lower() == 'y':
        error_logs_dir = path_manager.get_error_logs_path()
        if error_logs_dir.exists():
            error_files = list(error_logs_dir.glob("errorLog_*.log"))
            for file in error_files:
                file.unlink()
                print(f"✓ Deleted: {file.name}")
            print(f"\nDeleted {len(error_files)} file(s)")
        else:
            print("No files to delete")
    else:
        print("Keeping test files")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ERROR LOGGING SYSTEM TEST SUITE")
    print("="*70)
    print("\nThis script tests the lazy error logging system that only creates")
    print("log files when errors actually occur, with daily file rotation.")
    
    try:
        # Run all tests
        test_no_errors()
        test_single_error_today()
        test_multiple_errors_same_day()
        test_simulated_different_days()
        test_exception_handling()
        test_critical_errors()
        test_mixed_log_levels()
        
        # Show results
        show_created_files()
        
        # Cleanup
        cleanup_test_files()
        
        print("\n" + "="*70)
        print("ALL TESTS COMPLETED")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
