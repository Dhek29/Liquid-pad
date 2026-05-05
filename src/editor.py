"""
Text editor component for LiquidPad.
Handles the main text area with scrollbar and glass effects.
"""

import tkinter as tk
from effects import GlassEffects


class Editor:
    """Main text editing area with glass styling."""
    
    def __init__(self, parent, theme):
        """
        Initialize the editor.
        
        Args:
            parent: Parent tkinter widget
            theme: Theme dictionary
        """
        self.parent = parent
        self.theme = theme
        self.text_area = None
        
        self._build()
    
    def _build(self):
        """Construct the editor UI."""
        # Outer glass container
        glass_container = tk.Frame(
            self.parent,
            bg=self.theme["border"],
            bd=0
        )
        GlassEffects.apply_glass_border(glass_container, self.theme)
        glass_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(15, 0))
        
        # Inner glass panel
        glass_inner = tk.Frame(
            glass_container,
            bg=self.theme["text_bg"],
            bd=0
        )
        glass_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Apply glass overlay effect if enabled
        if self.theme.get("glass_effect"):
            GlassEffects.add_glass_overlay(glass_inner, self.theme)
        
        # Text widget - the core
        self.text_area = tk.Text(
            glass_inner,
            wrap=tk.WORD,
            undo=True,
            maxundo=50,
            bg=self.theme["text_bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["cursor"],
            selectbackground=self.theme["select_bg"],
            selectforeground=self.theme["fg"],
            relief=tk.FLAT,
            bd=0,
            padx=18,
            pady=12,
            font=('Cascadia Code', 11),
            highlightthickness=0,
            borderwidth=0
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar with theme styling
        scrollbar_width = 10 if self.theme.get("glass_effect") else 14
        scrollbar = tk.Scrollbar(
            glass_inner,
            bg=self.theme["accent"],
            troughcolor=self.theme["text_bg"],
            activebackground=self.theme["border"],
            width=scrollbar_width,
            relief=tk.FLAT
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=5)
        
        # Connect scrollbar to text area
        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)
        
        # Focus the text area
        self.text_area.focus_set()
    
    def get_text(self):
        """Get all text from editor."""
        return self.text_area.get("1.0", "end-1c")
    
    def set_text(self, content):
        """Set text in editor."""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
    
    def clear(self):
        """Clear all text."""
        self.text_area.delete("1.0", tk.END)
    
    def get_stats(self):
        """
        Get word and character count.
        
        Returns:
            Tuple of (word_count, character_count)
        """
        text = self.get_text()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        return words, chars
    
    def set_font_size(self, size):
        """Change font size."""
        self.text_area.configure(font=('Cascadia Code', size))
    
    def update_theme(self, theme):
        """Update editor with new theme."""
        self.theme = theme
        self.text_area.configure(
            bg=theme["text_bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
            selectbackground=theme["select_bg"],
            selectforeground=theme["fg"]
        )