"""
Script to replace print statements with debug_log calls
Run to convert all debug print statements
"""
import re
from pathlib import Path

files_to_update = [
    'src/core/path_manager.py',
    'src/core/config.py',
    'src/core/database.py',
    'src/core/activity_logger.py',
    'src/core/theme_manager.py',
]

# Pattern to match: print(f"[Category] message")
pattern = r'print\(f"\[([^\]]+)\]\s*([^"]+)"\)'

def replace_in_file(filepath):
    """Replace print statements in a file"""
    path = Path(filepath)
    if not path.exists():
        print(f"Skipping {filepath} - file not found")
        return
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    # Add import
    if 'from src.core.debug import debug_log' not in content:
        lines = content.split('\n')
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        lines.insert(last_import_idx + 1, 'from src.core.debug import debug_log')
        content = '\n'.join(lines)
    
    # Replace print statements
    def replacer(match):
        category = match.group(1)
        message = match.group(2)
        return f'debug_log(\'{category}\', f"{message}")'
    
    content = re.sub(pattern, replacer, content)
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"✓ Updated {filepath}")
    else:
        print(f"- No changes needed in {filepath}")

if __name__ == '__main__':
    print("Replacing print statements with debug_log calls...\n")
    for file in files_to_update:
        replace_in_file(file)
    print("\nDone! Set DEBUG_ENABLED = False in src/core/debug.py for clean terminal.")
