"""
Status bar component for LiquidPad.
Shows file info, word count, theme, opacity, selection stats, and file type.
"""

import tkinter as tk
import os


class StatusBar:
    """Bottom status bar displaying editor information."""
    
    FILE_TYPES = {
        '.py': ('🐍', 'Python'),
        '.js': ('📜', 'JavaScript'),
        '.html': ('🌐', 'HTML'),
        '.htm': ('🌐', 'HTML'),
        '.css': ('🎨', 'CSS'),
        '.json': ('📦', 'JSON'),
        '.xml': ('📋', 'XML'),
        '.md': ('📝', 'Markdown'),
        '.txt': ('📄', 'Text'),
        '.csv': ('📊', 'CSV'),
        '.sql': ('🗄️', 'SQL'),
        '.java': ('☕', 'Java'),
        '.cpp': ('⚙️', 'C++'),
        '.c': ('⚙️', 'C'),
        '.h': ('⚙️', 'C Header'),
        '.rs': ('🦀', 'Rust'),
        '.go': ('🔷', 'Go'),
        '.rb': ('💎', 'Ruby'),
        '.php': ('🐘', 'PHP'),
        '.swift': ('🍎', 'Swift'),
        '.kt': ('📱', 'Kotlin'),
        '.ts': ('📘', 'TypeScript'),
        '.tsx': ('⚛️', 'React TSX'),
        '.jsx': ('⚛️', 'React JSX'),
        '.vue': ('💚', 'Vue'),
        '.yaml': ('📝', 'YAML'),
        '.yml': ('📝', 'YAML'),
        '.toml': ('⚙️', 'TOML'),
        '.ini': ('⚙️', 'Config'),
        '.cfg': ('⚙️', 'Config'),
        '.sh': ('🐚', 'Shell'),
        '.bash': ('🐚', 'Bash'),
        '.bat': ('🪟', 'Batch'),
        '.ps1': ('💙', 'PowerShell'),
        '.env': ('🔐', 'Environment'),
        '.log': ('📋', 'Log'),
    }
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.bar = None
        self._build()
    
    def _build(self):
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
    
    def detect_file_type(self, filename):
        """Detect file type from filename or path."""
        if not filename or filename == "Untitled":
            return ('📄', '')
        
        base = os.path.basename(filename)
        _, ext = os.path.splitext(base)
        ext = ext.lower()
        
        base_lower = base.lower()
        if base_lower in self.FILE_TYPES:
            return self.FILE_TYPES[base_lower]
        
        if ext in self.FILE_TYPES:
            return self.FILE_TYPES[ext]
        
        return ('📄', '')
    
    def update(self, filename, words, chars, theme_name, opacity, sel_words=0, sel_chars=0):
        """Update status bar with clean display."""
        if sel_words > 0 or sel_chars > 0:
            stats = f"Words: {sel_words}/{words} selected | Characters: {sel_chars}/{chars}"
        else:
            stats = f"Words: {words} | Characters: {chars}"
        
        # Get clean name for display
        if filename and filename != "Untitled":
            display_name = os.path.basename(filename)
        else:
            display_name = "Untitled"
        
        # Detect file type
        file_icon, file_type = self.detect_file_type(filename)
        
        # Build display
        if file_type:
            file_display = f"{file_icon} {display_name} | {file_type}"
        else:
            file_display = f"📄 {display_name}"
        
        text = (
            f"💧 LiquidPad | {file_display} | "
            f"{stats} | "
            f"{theme_name} | Opacity: {opacity}%"
        )
        self.bar.config(text=text)
    
    def update_theme(self, theme):
        self.theme = theme
        self.bar.configure(
            bg=theme["accent"],
            fg=theme["fg"]
        )
