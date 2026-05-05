"""
LiquidPad - Main application class.
Ties together all components: editor, statusbar, menubar, themes.
"""

import tkinter as tk
import os
from tkinter import messagebox
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from menubar import MenuBar
from session import SessionManager


class LiquidPad:
    """Main LiquidPad application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPad - Untitled")
        self.root.geometry("900x650")
        self.root.attributes('-alpha', 0.92)
        
        # Store reference for child components to access app
        self.root._app = self
        
        # Set icon
        self._set_icon()
        
        # Theme management
        self.themes = THEMES
        self.current_theme_name = DEFAULT_THEME
        self.current_theme = self.themes[self.current_theme_name]
        
        # Set background
        self.root.configure(bg=self.current_theme["bg"])
        
        # Build components
        self._build_ui()
        
        # Center window on screen
        self._center_window()
        
        # Bind typing event to update status
        self.root.bind('<KeyRelease>', lambda e: self._update_status())
        self.root.bind('<ButtonRelease-1>', lambda e: self._update_status())
        
        # Setup session management (after UI is fully built)
        self.setup_session_manager()
    
    def _set_icon(self):
        """Set window icon from assets folder."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass
    
    def _build_ui(self):
        """Build all UI components."""
        # Status bar (bottom)
        self.statusbar = StatusBar(self.root, self.current_theme)
        
        # Editor (main area)
        self.editor = Editor(self.root, self.current_theme)
        
        # Menu bar (top)
        self.menubar = MenuBar(self.root, self.editor, self.statusbar, self._change_theme)
        self.menubar.setup(self.themes, self.current_theme_name)
        
        # Initial status update
        self._update_status()
    
    def _center_window(self):
        """Center the window on screen."""
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def _change_theme(self, theme_name):
        """Switch to a different theme."""
        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]
        
        self.root.configure(bg=self.current_theme["bg"])
        self.editor.update_theme(self.current_theme)
        self.statusbar.update_theme(self.current_theme)
        self.menubar.rebuild(theme_name)
        self._update_status()
    
    def _update_status(self):
        """Update the status bar with current editor info."""
        words, chars = self.editor.get_stats()
        sel_words, sel_chars = self.editor.get_selection_stats()
        filename = self.menubar.get_full_filename()
        theme_name = self.themes[self.current_theme_name]["name"]
        opacity = self.menubar.get_opacity()
        
        self.statusbar.update(filename, words, chars, theme_name, opacity, sel_words, sel_chars)
    
    # ========================
    # SESSION RECOVERY METHODS
    # ========================
    
    def setup_session_manager(self):
        """Initialize session and recovery system."""
        self.session_manager = SessionManager(self)
    
    def check_session_recovery(self):
        """Check and offer to restore previous session."""
        recovery_text = self.session_manager.check_recovery()
        
        if recovery_text:
            restored = messagebox.askyesno(
                "LiquidPad - Session Recovery",
                "⚠️ Unsaved work detected from previous session.\n\n"
                "Would you like to restore it?\n\n"
                "Click 'No' to discard and start fresh."
            )
            
            if restored:
                self.editor.set_text(recovery_text)
                self.root.title("LiquidPad - [Recovered]")
            else:
                self.session_manager.clear_recovery()
        
        if not self.session_manager.session_loaded:
            state = self.session_manager.load_session_state()
            if state:
                self.session_manager.restore_session(state)
        
        self.session_manager.start_auto_save()
    
    def on_close(self):
        """Handle application close event."""
        self.session_manager.save_session_state()
        
        if not self.editor.get_text().strip():
            self.session_manager.clear_recovery()
        
        self.root.destroy()
