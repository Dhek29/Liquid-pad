"""
Status bar component for LiquidPad.
Shows file info, word count, theme, and opacity.
"""

import tkinter as tk


class StatusBar:
    """Bottom status bar displaying editor information."""
    
    def __init__(self, parent, theme):
        """
        Initialize the status bar.
        
        Args:
            parent: Parent tkinter widget
            theme: Theme dictionary
        """
        self.parent = parent
        self.theme = theme
        self.bar = None
        
        self._build()
    
    def _build(self):
        """Construct the status bar."""
        self.bar = tk.Label(
            self.parent,
            text="💧 LiquidPad Ready",
            bg=self.theme["accent"],
            fg=self.theme["fg"],
            anchor=tk.W,
            padx=12,
            pady=5,
            font=('Segoe UI', 8)
        )
        self.bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update(self, filename, words, chars, theme_name, opacity):
        """
        Update status bar text.
        
        Args:
            filename: Current file name or 'Untitled'
            words: Word count
            chars: Character count
            theme_name: Current theme display name
            opacity: Transparency percentage
        """
        text = (
            f"💧 LiquidPad | {filename} | "
            f"Words: {words} | Characters: {chars} | "
            f"{theme_name} | Opacity: {opacity}%"
        )
        self.bar.config(text=text)
    
    def update_theme(self, theme):
        """Update status bar colors for new theme."""
        self.theme = theme
        self.bar.configure(
            bg=theme["accent"],
            fg=theme["fg"]
        )