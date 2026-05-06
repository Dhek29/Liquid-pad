"""
Session management for LiquidPad.
Handles auto-save, crash recovery, state persistence, and recent files.
Completely standalone - works with any LiquidPad version.
"""

import json
import os
import time


class SessionManager:
    """Manages application session state and auto-save recovery."""
    
    def __init__(self, app_instance):
        """
        Initialize session manager.
        
        Args:
            app_instance: The main LiquidPad instance
        """
        self.app = app_instance
        self.config_dir = self._get_config_dir()
        self.config_file = os.path.join(self.config_dir, 'liquidpad_config.json')
        self.recovery_file = os.path.join(self.config_dir, '.liquidpad_recovery.txt')
        
        # Auto-save settings
        self.auto_save_interval = 5  # seconds
        self.auto_save_job = None
        self.last_save_time = 0
        self.session_loaded = False
        
        # Recent files
        self.max_recent_files = 10
        self.recent_files = []
        
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
    
    def _get_config_dir(self):
        """Get the config directory path."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_dir = os.path.join(base_dir, 'config')
        return config_dir
    
    def save_session_state(self):
        """Save current session state to config file."""
        try:
            state = {
                'theme': self.app.current_theme_name,
                'opacity': self.app.menubar.get_opacity(),
                'last_file': self.app.menubar.current_file,
                'recent_files': self.recent_files,
                'window_geometry': self.app.root.geometry(),
                'timestamp': time.time()
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            print(f"Session save error (non-critical): {e}")
    
    def load_session_state(self):
        """Load previous session state including recent files."""
        if not os.path.exists(self.config_file):
            return None
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Load recent files
            self.recent_files = state.get('recent_files', [])
            # Clean up files that no longer exist
            self.recent_files = [f for f in self.recent_files if os.path.exists(f)]
            
            return state
        except Exception:
            return None
    
    def add_recent_file(self, filepath):
        """Add a file to recent files list."""
        if not filepath:
            return
        
        # Convert to absolute path
        filepath = os.path.abspath(filepath)
        
        # Remove if already in list (we'll add to top)
        if filepath in self.recent_files:
            self.recent_files.remove(filepath)
        
        # Add to front
        self.recent_files.insert(0, filepath)
        
        # Keep only max_recent_files
        self.recent_files = self.recent_files[:self.max_recent_files]
        
        # Save immediately
        self.save_session_state()
        
        # Rebuild menu to show updated list
        if hasattr(self.app, 'menubar'):
            self.app.menubar._create_menus()
    
    def clear_recent_files(self):
        """Clear the recent files list."""
        self.recent_files = []
        self.save_session_state()
        
        # Rebuild menu
        if hasattr(self.app, 'menubar'):
            self.app.menubar._create_menus()
    
    def get_recent_files(self):
        """Get list of existing recent files."""
        # Filter to only existing files
        return [f for f in self.recent_files if os.path.exists(f)]
    
    def check_recovery(self):
        """Check if there's unsaved work to recover."""
        if os.path.exists(self.recovery_file):
            try:
                with open(self.recovery_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():
                    return content
            except Exception:
                pass
        
        return None
    
    def auto_save_backup(self):
        """Auto-save current text to recovery file."""
        try:
            current_text = self.app.editor.get_text()
            
            if current_text.strip():
                with open(self.recovery_file, 'w', encoding='utf-8') as f:
                    f.write(current_text)
                self.last_save_time = time.time()
        except Exception as e:
            print(f"Auto-save error (non-critical): {e}")
    
    def clear_recovery(self):
        """Clear the recovery file (called on clean save/exit)."""
        try:
            if os.path.exists(self.recovery_file):
                os.remove(self.recovery_file)
        except Exception:
            pass
    
    def start_auto_save(self):
        """Start the periodic auto-save timer."""
        self._schedule_auto_save()
    
    def _schedule_auto_save(self):
        """Schedule next auto-save."""
        if self.auto_save_job:
            self.app.root.after_cancel(self.auto_save_job)
        
        self.auto_save_backup()
        
        self.auto_save_job = self.app.root.after(
            self.auto_save_interval * 1000, 
            self._schedule_auto_save
        )
    
    def restore_session(self, state):
        """Restore previous session settings."""
        if not state:
            return
        
        try:
            theme_name = state.get('theme', 'glass')
            if theme_name in self.app.themes:
                self.app._change_theme(theme_name)
            
            opacity = state.get('opacity', 92)
            self.app.root.attributes('-alpha', opacity / 100)
            
            geometry = state.get('window_geometry')
            if geometry:
                try:
                    self.app.root.geometry(geometry)
                except Exception:
                    pass
            
            self.session_loaded = True
        except Exception as e:
            print(f"Session restore error (non-critical): {e}")
    
    def on_clean_exit(self):
        """Handle clean application exit."""
        self.save_session_state()
        self.clear_recovery()