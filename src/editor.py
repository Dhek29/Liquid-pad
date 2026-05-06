"""
Text editor component for LiquidPad.
Handles the main text area with scrollbar, glass effects, line numbers,
right-click context menu, zoom, selection stats, and snippets.

IMPORTANT: Editor.__init__ does NOT pack glass_container.
           TabManager is the sole owner of when/how it gets packed.
"""

import tkinter as tk
import webbrowser
from effects import GlassEffects
from linenumbers import LineNumbers
from snippets import SnippetManager


class Editor:
    """Main text editing area with glass styling."""
    
    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.text_area = None
        self.line_numbers = None
        self.glass_container = None
        self.current_font_size = 11
        self.snippet_manager = SnippetManager()
        
        self._build()
    
    def _build(self):
        """Construct the editor UI.
        
        NOTE: glass_container is intentionally NOT packed here.
              TabManager calls .pack() / .pack_forget() exclusively.
        """
        self.glass_container = tk.Frame(
            self.parent,
            bg=self.theme["border"],
            bd=0
        )
        GlassEffects.apply_glass_border(self.glass_container, self.theme)
        # *** DO NOT call self.glass_container.pack() here ***
        # TabManager._switch_to_index() owns all pack/pack_forget calls.
        
        glass_inner = tk.Frame(
            self.glass_container,
            bg=self.theme["text_bg"],
            bd=0
        )
        glass_inner.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        if self.theme.get("glass_effect"):
            GlassEffects.add_glass_overlay(glass_inner, self.theme)
        
        text_frame = tk.Frame(glass_inner, bg=self.theme["text_bg"], bd=0)
        text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
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
        
        self._bind_zoom()
        self._bind_context_menu()
        self._bind_snippets()
        
        self.line_numbers = LineNumbers(text_frame, self.text_area, self.theme)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
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
        
        self.text_area.config(yscrollcommand=self._on_scroll)
        self._scrollbar.config(command=self._scroll_both)
        
        self.text_area.focus_set()
    
    # ====================
    # CONTEXT MENU
    # ====================
    
    def _bind_context_menu(self):
        self.text_area.bind('<Button-2>', self._show_context_menu)
        self.text_area.bind('<Button-3>', self._show_context_menu)
    
    def _show_context_menu(self, event):
        menu = tk.Menu(self.text_area, tearoff=0,
                      bg=self.theme["bg"],
                      fg=self.theme["fg"],
                      activebackground=self.theme["accent"],
                      activeforeground=self.theme["fg"],
                      font=('Segoe UI', 9))
        
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            has_selection = bool(selected_text.strip())
        except tk.TclError:
            has_selection = False
            selected_text = ""
        
        menu.add_command(label="✂️  Cut", command=self._cut, accelerator="Ctrl+X")
        
        if has_selection:
            menu.add_command(label="📋  Copy", command=self._copy, accelerator="Ctrl+C")
        else:
            menu.add_command(label="📋  Copy", state=tk.DISABLED, accelerator="Ctrl+C")
        
        try:
            clipboard = self.text_area.clipboard_get()
            has_clipboard = bool(clipboard.strip())
        except:
            has_clipboard = False
        
        if has_clipboard:
            menu.add_command(label="📄  Paste", command=self._paste, accelerator="Ctrl+V")
        else:
            menu.add_command(label="📄  Paste", state=tk.DISABLED, accelerator="Ctrl+V")
        
        menu.add_separator()
        menu.add_command(label="🔲  Select All", command=self._select_all, accelerator="Ctrl+A")
        
        if has_selection:
            menu.add_command(label="🗑️  Clear Selection", command=self._clear_selection)
        
        menu.add_separator()
        menu.add_command(label="↩️  Undo", command=self._undo, accelerator="Ctrl+Z")
        menu.add_command(label="↪️  Redo", command=self._redo, accelerator="Ctrl+Y")
        
        if has_selection:
            menu.add_separator()
            menu.add_command(
                label="🌐  Search Web for Selection",
                command=lambda: self._search_web(selected_text)
            )
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _search_web(self, text):
        query = text.strip().replace(' ', '+')
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
    
    def _clear_selection(self):
        try:
            self.text_area.tag_remove(tk.SEL, "1.0", tk.END)
        except:
            pass
    
    # ====================
    # SNIPPETS
    # ====================
    
    def _bind_snippets(self):
        self.text_area.bind('<Tab>', self._expand_snippet)
    
    def _expand_snippet(self, event):
        cursor_pos = self.text_area.index(tk.INSERT)
        line_start = f"{cursor_pos.split('.')[0]}.0"
        current_line = self.text_area.get(line_start, cursor_pos)
        
        words = current_line.split()
        if not words:
            self.text_area.insert(tk.INSERT, '    ')
            return 'break'
        
        last_word = words[-1]
        expanded = self.snippet_manager.expand(last_word)
        
        if expanded:
            trigger_start = f"{line_start}+{current_line.rindex(last_word)}c"
            self.text_area.delete(trigger_start, cursor_pos)
            self.text_area.insert(trigger_start, expanded)
            return 'break'
        
        self.text_area.insert(tk.INSERT, '    ')
        return 'break'
    
    # ====================
    # ZOOM
    # ====================
    
    def _bind_zoom(self):
        self.text_area.bind('<Control-MouseWheel>', self._zoom)
        self.text_area.bind('<Control-Button-4>', self._zoom)
        self.text_area.bind('<Control-Button-5>', self._zoom)
    
    def _zoom(self, event):
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
        self.line_numbers._update()
        self._scrollbar.set(*args)
    
    def _scroll_both(self, *args):
        self.text_area.yview(*args)
        self.line_numbers._update()
    
    # ====================
    # CORE METHODS
    # ====================
    
    def get_text(self):
        return self.text_area.get("1.0", "end-1c")
    
    def set_text(self, content):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)
        self.line_numbers._update()
    
    def clear(self):
        self.text_area.delete("1.0", tk.END)
        self.line_numbers._update()
    
    def get_stats(self):
        text = self.get_text()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        return words, chars
    
    def get_selection_stats(self):
        try:
            selected_text = self.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
            words = len(selected_text.split()) if selected_text.strip() else 0
            chars = len(selected_text)
            return words, chars
        except tk.TclError:
            return 0, 0
    
    def set_font_size(self, size):
        self.current_font_size = size
        self.text_area.configure(font=('Cascadia Code', size))
        if self.line_numbers:
            self.line_numbers.set_font_size(size)
    
    def update_theme(self, theme):
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
        try: self.text_area.edit_undo()
        except: pass
    
    def _redo(self):
        try: self.text_area.edit_redo()
        except: pass
    
    def _cut(self):
        self.text_area.event_generate("<<Cut>>")
    
    def _copy(self):
        self.text_area.event_generate("<<Copy>>")
    
    def _paste(self):
        self.text_area.event_generate("<<Paste>>")
    
    def _select_all(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")