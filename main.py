"""
Lifeboat - Personal Life Management Application
Main entry point
"""
import sys
from src.ui.app import LifeboatApp

def main():
    """Main entry point"""
    try:
        app = LifeboatApp()
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
