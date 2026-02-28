"""
Simple Custom Updater for Lifeboat
Checks GitHub releases for updates
"""
import requests
import json
from typing import Optional, Dict
from pathlib import Path

from src.core.constants import APP_VERSION


class Updater:
    """Simple updater that checks GitHub releases"""
    
    # GitHub repository info
    GITHUB_USER = "faiz-n-shk"
    GITHUB_REPO = "LifeBoat"
    
    # API endpoints
    RELEASES_API = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"
    
    def __init__(self):
        self.current_version = APP_VERSION
        self.latest_version = None
        self.download_url = None
        self.release_notes = None
    
    def check_for_updates(self, timeout: int = 10) -> Optional[Dict]:
        """
        Check if a new version is available
        
        Returns:
            Dict with update info if available, None otherwise
            {
                'available': bool,
                'current_version': str,
                'latest_version': str,
                'download_url': str,
                'release_notes': str,
                'release_date': str
            }
        """
        try:
            # Make request to GitHub API
            response = requests.get(
                self.RELEASES_API,
                timeout=timeout,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Extract version from tag (e.g., "v2.8.0" -> "2.8.0")
            tag_name = data.get('tag_name', '')
            latest_version = tag_name.lstrip('v')
            
            # Get download URL for installer
            download_url = None
            for asset in data.get('assets', []):
                # Look for installer executable
                if asset['name'].endswith('.exe'):
                    download_url = asset['browser_download_url']
                    break
            
            # If no .exe found, use the release page
            if not download_url:
                download_url = data.get('html_url')
            
            # Check if update is available
            is_newer = self._compare_versions(latest_version, self.current_version)
            
            return {
                'available': is_newer,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'download_url': download_url,
                'release_notes': data.get('body', 'No release notes available'),
                'release_date': data.get('published_at', '')
            }
            
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None
    
    def _compare_versions(self, version1: str, version2: str) -> bool:
        """
        Compare two version strings
        
        Returns:
            True if version1 > version2
        """
        try:
            # Split versions into parts
            v1_parts = [int(x) for x in version1.split('.')]
            v2_parts = [int(x) for x in version2.split('.')]
            
            # Pad shorter version with zeros
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            # Compare
            return v1_parts > v2_parts
            
        except (ValueError, AttributeError):
            return False
    
    def open_download_page(self):
        """Open the download page in browser"""
        import webbrowser
        if self.download_url:
            webbrowser.open(self.download_url)
        else:
            # Fallback to releases page
            url = f"https://github.com/{self.GITHUB_USER}/{self.GITHUB_REPO}/releases/latest"
            webbrowser.open(url)
