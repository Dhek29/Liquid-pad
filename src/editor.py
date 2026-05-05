"""
Text editor component for LiquidPad.
Handles the main text area with scrollbar, glass effects, line numbers,
right-click context menu, zoom, and selection stats.
"""

import tkinter as tk
import webbrowser
from effects import GlassEffects
from linenumbers import LineNumbers


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
        self.line_numbers = None
        self.current_font_size = 11
        
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
        
        # Text + Line numbers container
        text_frame = tk.Frame(glass_inner, bg=self.theme["text_bg"], bd=0)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Text widget - the core
        self.text_area = tk.Text(
            text_frame,
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
            padx=15,
            pady=12,
            font=('Cascadia Code', 11),
            highlightthickness=0,
            borderwidth=0
        )
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Bind Ctrl+Scroll for zoom
        self._bind_zoom()
        
        # Bind right-click context menu
        self._bind_context_menu()
        
        # Line numbers
        self.line_numbers = LineNumbers(text_frame, self.text_area, self.theme)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Scrollbar with theme styling
        scrollbar_width = 10 if self.theme.get("glass_effect") else 14
        self._scrollbar = tk.Scrollbar(
            glass_inner,
            bg=self.theme["accent"],
            troughcolor=self.theme["text_bg"],
            activebackground=self.theme["border"],
            width=scrollbar_width,
            relief=tk.FLAT
        )
        self._scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 2), pady=5)
        
        # Connect scrollbar to text area
        self.text_area.config(yscrollcommand=self._on_scroll)
        self._scrollbar.config(command=self._scroll_both)
        
        # Focus the text area
        self.text_area.focus_set()
    
    # ====================
    # CONTEXT MENU
    # ====================
    
    def _bind_context_menu(self):
        """Bind right-click to show context menu."""
        self.text_area.bind('<Button-2>', self._show_context_menu)  # macOS
        self.text_area.bind('<Button-3>', self._show_context_menu)  # Windows/Linux
    
    def _show_context_menu(self, event):
        """Show the right-click context menu."""
        menu = tk.Menu(self.text_area, tearoff=0,
                      bg=self.theme["bg"],
                      fg=self.theme["fg"],
                      activebackground=self.theme["accent"],
                      activeforeground=self.theme["fg"],
                      font=('Segoe UI', 9))
        
        # Check if text is selected
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            has_selection = bool(selected_text.strip())
        except tk.TclError:
            has_selection = False
            selected_text = ""
        
        # Cut
        menu.add_command(
            label="✂️  Cut",
            command=self._cut,
            accelerator="Ctrl+X"
        )
        
        # Copy
        if has_selection:
            menu.add_command(
                label="📋  Copy",
                command=self._copy,
                accelerator="Ctrl+C"
            )
        else:
            menu.add_command(
                label="📋  Copy",
                state=tk.DISABLED,
                accelerator="Ctrl+C"
            )
        
        # Paste
        try:
            clipboard = self.text_area.clipboard_get()
            has_clipboard = bool(clipboard.strip())
        except:
            has_clipboard = False
        
        if has_clipboard:
            menu.add_command(
                label="📄  Paste",
                command=self._paste,
                accelerator="Ctrl+V"
            )
        else:
            menu.add_command(
                label="📄  Paste",
                state=tk.DISABLED,
                accelerator="Ctrl+V"
            )
        
        menu.add_separator()
        
        # Select All
        menu.add_command(
            label="🔲  Select All",
            command=self._select_all,
            accelerator="Ctrl+A"
        )
        
        # Clear Selection
        if has_selection:
            menu.add_command(
                label="🗑️  Clear Selection",
                command=self._clear_selection
            )
        
        # Undo / Redo
        menu.add_separator()
        menu.add_command(
            label="↩️  Undo",
            command=self._undo,
            accelerator="Ctrl+Z"
        )
        menu.add_command(
            label="↪️  Redo",
            command=self._redo,
            accelerator="Ctrl+Y"
        )
        
        # Search Google for selected text
        if has_selection:
            menu.add_separator()
            menu.add_command(
                label="🌐  Search Web for Selection",
                command=lambda: self._search_web(selected_text)
            )
        
        # Show at cursor position
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _search_web(self, text):
        """Search selected text on Google."""
        query = text.strip().replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
    
    def _clear_selection(self):
        """Clear current text selection."""
        try:
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass
    
    # ====================
    # ZOOM
    # ====================
    
    def _bind_zoom(self):
        """Bind Ctrl+MouseWheel for zoom in/out."""
        self.text_area.bind('<Control-MouseWheel>', self._zoom)
        self.text_area.bind('<Control-Button-4>', self._zoom)
        self.text_area.bind('<Control-Button-5>', self._zoom)
    
    def _zoom(self, event):
        """Handle zoom in/out with Ctrl+Scroll."""
        if event.delta:
            delta = event.delta
        elif event.num == 4:
            delta = 120
        elif event.num == 5:
            delta = -120
        else:
            return
        
        if delta > 0:
            self.current_font_size = min(24, self.current_font_size + 1)
        else:
            self.current_font_size = max(8, self.current_font_size - 1)
        
        self.set_font_size(self.current_font_size)
        return 'break'
    
    # ====================
    # SCROLL SYNC
    # ====================
    
    def _on_scroll(self, *args):
        """Handle text scroll and update line numbers."""
        self.line_numbers._update()
        self._scrollbar.set(*args)
    
    def _scroll_both(self, *args):
        """Scroll both text area and update line numbers."""
        self.text_area.yview(*args)
        self.line_numbers._update()
    
    # ====================
    # CORE METHODS
    # ====================
    
    def get_text(self):
        """Get all text from editor."""
        return self.text_area.get("1.0", "end-1c")
    
    def set_text(self, content):
        """Set text in editor."""
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        self.line_numbers._update()
    
    def clear(self):
        """Clear all text."""
        self.text_area.delete("1.0", tk.END)
        self.line_numbers._update()
    
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
    
    def get_selection_stats(self):
        """
        Get word and character count for selected text.
        
        Returns:
            Tuple of (selected_words, selected_chars) or (0, 0) if no selection
        """
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            words = len(selected_text.split()) if selected_text.strip() else 0
            chars = len(selected_text)
            return words, chars
        except tk.TclError:
            return 0, 0
    
    def set_font_size(self, size):
        """Change font size."""
        self.current_font_size = size
        self.text_area.configure(font=('Cascadia Code', size))
        if self.line_numbers:
            self.line_numbers.set_font_size(size)
    
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
        if self.line_numbers:
            self.line_numbers.update_theme(theme)
    
    # ====================
    # EDIT OPERATIONS
    # ====================
    
    def _undo(self):
        """Undo last edit."""
        try:
            self.text_area.edit_undo()
        except:
            pass
    
    def _redo(self):
        """Redo last undo."""
        try:
            self.text_area.edit_redo()
        except:
            pass
    
    def _cut(self):
        """Cut selected text."""
        self.text_area.event_generate("<<Cut>>")
    
    def _copy(self):
        """Copy selected text."""
        self.text_area.event_generate("<<Copy>>")
    
    def _paste(self):
        """Paste from clipboard."""
        self.text_area.event_generate("<<Paste>>")
    
    def _select_all(self):
        """Select all text."""
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
