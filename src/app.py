"""
LiquidPad - Main application class.
Ties together all components: editor, statusbar, menubar, themes.
"""

import tkinter as tk
import os
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from menubar import MenuBar


class LiquidPad:
    """Main LiquidPad application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPad - Untitled")
        self.root.geometry("900x650")
        self.root.attributes('-alpha', 0.92)
        
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
        
        # Update root window
        self.root.configure(bg=self.current_theme["bg"])
        
        # Update components
        self.editor.update_theme(self.current_theme)
        self.statusbar.update_theme(self.current_theme)
        self.menubar.rebuild(theme_name)
        
        # Update status display
        self._update_status()
    
    def _update_status(self):
        """Update the status bar with current editor info."""
        words, chars = self.editor.get_stats()
        filename = self.menubar.get_filename()
        theme_name = self.themes[self.current_theme_name]["name"]
        opacity = self.menubar.get_opacity()
        
        self.statusbar.update(filename, words, chars, theme_name, opacity)