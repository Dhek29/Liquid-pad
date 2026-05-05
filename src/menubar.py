"""
Menu bar component for LiquidPad.
Creates all menus and keyboard shortcuts.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from findreplace import FindReplace


class MenuBar:
    """Application menu bar with File, Edit, View, and Help menus."""
    
    def __init__(self, root, editor, statusbar, theme_callback):
        self.root = root
        self.editor = editor
        self.statusbar = statusbar
        self.change_theme = theme_callback
        self.current_file = None
        self.themes = {}
        self.current_theme_name = "glass"
        self.find_replace = None
        
    def setup(self, themes, theme_name):
        """Set themes and build menus."""
        self.themes = themes
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        self.find_replace = FindReplace(self.root, self.editor)
    
    def rebuild(self, theme_name):
        """Rebuild menus after theme change."""
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        if self.find_replace:
            self.find_replace.set_theme(self._theme())
    
    def _theme(self):
        """Get current theme safely."""
        return self.themes.get(self.current_theme_name, {
            "bg": "#1a1a2e", "fg": "#ffffff", "accent": "#333333", "text_bg": "#1e1e3a"
        })
    
    def _create_menus(self):
        """Create all menus."""
        t = self._theme()
        
        blank = tk.Menu(self.root)
        self.root.config(menu=blank)
        
        menubar = tk.Menu(
            self.root,
            bg=t["bg"],
            fg=t["fg"],
            activebackground=t["accent"],
            activeforeground=t["fg"],
            relief=tk.FLAT,
            bd=0,
            font=('Segoe UI', 9)
        )
        self.root.config(menu=menubar)
        
        # === FILE MENU ===
        file_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self._new, accelerator="Ctrl+N")
        file_menu.add_command(label="Open", command=self._open, accelerator="Ctrl+O")
        
        # Recent Files
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                                    activebackground=t["accent"], activeforeground=t["fg"])
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        self._build_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit, accelerator="Ctrl+Q")
        
        # === EDIT MENU ===
        edit_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=self._undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=self._redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=self._cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=self._copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=self._paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_separator()
        edit_menu.add_command(label="Find & Replace", command=self._show_find_replace, accelerator="Ctrl+F")
        
        # === VIEW MENU ===
        view_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="View", menu=view_menu)
        
        trans_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                            activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Transparency", menu=trans_menu)
        for pct in [95, 90, 85, 80, 75, 70, 60, 50]:
            trans_menu.add_command(
                label=f"{pct}%",
                command=lambda v=pct: self._set_opacity(v/100)
            )
        
        theme_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                            activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Themes", menu=theme_menu)
        
        glass = [(k, v) for k, v in self.themes.items() if v.get("glass_effect")]
        normal = [(k, v) for k, v in self.themes.items() if not v.get("glass_effect")]
        
        for key, data in glass:
            theme_menu.add_command(label=data["name"], command=self._theme_switcher(key))
        if glass:
            theme_menu.add_separator()
        for key, data in normal:
            theme_menu.add_command(label=data["name"], command=self._theme_switcher(key))
        
        font_menu = tk.Menu(view_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        view_menu.add_cascade(label="Font Size", menu=font_menu)
        for size in [8, 9, 10, 11, 12, 14, 16, 18, 20, 24]:
            font_menu.add_command(label=f"{size} pt", command=self._font_switcher(size))
        
        # === HELP MENU ===
        help_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About LiquidPad", command=self._about)
        help_menu.add_command(label="Shortcuts", command=self._shortcuts)
    
    def _build_recent_files_menu(self):
        """Build the recent files submenu."""
        self.recent_menu.delete(0, tk.END)
        
        recent_files = []
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
            recent_files = self.root._app.session_manager.get_recent_files()
        
        if recent_files:
            for filepath in recent_files:
                dirname = os.path.dirname(filepath)
                basename = os.path.basename(filepath)
                parent_dir = os.path.basename(dirname)
                
                if parent_dir:
                    display_name = f"📄 {basename}  ({parent_dir})"
                else:
                    display_name = f"📄 {basename}"
                
                self.recent_menu.add_command(
                    label=display_name,
                    command=lambda fp=filepath: self._open_recent(fp)
                )
            
            self.recent_menu.add_separator()
            self.recent_menu.add_command(
                label="🗑️ Clear Recent Files",
                command=self._clear_recent_files
            )
        else:
            self.recent_menu.add_command(
                label="(No recent files)",
                state=tk.DISABLED
            )
    
    def _open_recent(self, filepath):
        """Open a file from recent files list."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.editor.set_text(f.read())
                self.current_file = filepath
                self.root.title(f"LiquidPad - {os.path.basename(filepath)}")
                
                if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
                    self.root._app.session_manager.add_recent_file(filepath)
                    self._build_recent_files_menu()
                
                # Update status bar
                if hasattr(self.root, '_app'):
                    self.root._app._update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showwarning("File Not Found", 
                f"This file no longer exists:\n{filepath}")
    
    def _clear_recent_files(self):
        """Clear all recent files."""
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
            self.root._app.session_manager.clear_recent_files()
            self._build_recent_files_menu()
    
    def _add_to_recent(self, filepath):
        """Add a file to recent files via session manager."""
        if not filepath:
            return
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
            self.root._app.session_manager.add_recent_file(filepath)
            self._build_recent_files_menu()
    
    def _theme_switcher(self, name):
        return lambda: self.change_theme(name)
    
    def _font_switcher(self, size):
        return lambda: self.editor.set_font_size(size)
    
    def _bind_keys(self):
        """Bind keyboard shortcuts."""
        self.root.bind('<Control-n>', lambda e: self._new())
        self.root.bind('<Control-o>', lambda e: self._open())
        self.root.bind('<Control-s>', lambda e: self._save())
        self.root.bind('<Control-S>', lambda e: self._save_as())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-f>', lambda e: self._show_find_replace())
    
    def _show_find_replace(self):
        """Show the Find & Replace dialog."""
        if self.find_replace:
            self.find_replace.set_theme(self._theme())
            self.find_replace.show()
    
    # ---- Actions ----
    
    def _set_opacity(self, value):
        self.root.attributes('-alpha', value)
    
    def _new(self):
        if self.editor.get_text().strip():
            if messagebox.askyesno("LiquidPad", "Save before new file?"):
                self._save()
        self.editor.clear()
        self.current_file = None
        self.root.title("LiquidPad - Untitled")
        # Update status bar
        if hasattr(self.root, '_app'):
            self.root._app._update_status()
    
    def _open(self):
        """Open a file with all file types visible."""
        path = filedialog.askopenfilename(
            title="Open File",
            filetypes=[
                ("All files", "*.*"),
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("JavaScript", "*.js"),
                ("HTML/CSS", "*.html *.htm *.css"),
                ("JSON", "*.json"),
                ("Markdown", "*.md"),
                ("SQL", "*.sql"),
                ("All code files", "*.py *.js *.html *.css *.json *.md *.sql *.java *.cpp *.c *.go *.rs")
            ]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.set_text(f.read())
            self.current_file = path
            self.root.title(f"LiquidPad - {os.path.basename(path)}")
            self._add_to_recent(path)
            # Update status bar for file type detection
            if hasattr(self.root, '_app'):
                self.root._app._update_status()
    
    def _save(self):
        if self.current_file:
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.root.title(f"LiquidPad - {os.path.basename(self.current_file)}")
            self._add_to_recent(self.current_file)
            # Update status bar for file type detection
            if hasattr(self.root, '_app'):
                self.root._app._update_status()
        else:
            self._save_as()
    
    def _save_as(self):
        path = filedialog.asksaveasfilename(
            title="Save As",
            defaultextension=".txt",
            filetypes=[
                ("All files", "*.*"),
                ("Python files", "*.py"),
                ("Text files", "*.txt"),
                ("JavaScript", "*.js"),
                ("HTML/CSS", "*.html *.htm *.css"),
                ("JSON", "*.json"),
                ("Markdown", "*.md"),
                ("SQL", "*.sql")
            ]
        )
        if path:
            self.current_file = path
            self._save()
    
    def _undo(self):
        try:
            self.editor.text_area.edit_undo()
        except:
            pass
    
    def _redo(self):
        try:
            self.editor.text_area.edit_redo()
        except:
            pass
    
    def _cut(self):
        self.editor.text_area.event_generate("<<Cut>>")
    
    def _copy(self):
        self.editor.text_area.event_generate("<<Copy>>")
    
    def _paste(self):
        self.editor.text_area.event_generate("<<Paste>>")
    
    def _select_all(self):
        self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.text_area.mark_set(tk.INSERT, "1.0")
    
    def get_filename(self):
        return os.path.basename(self.current_file) if self.current_file else "Untitled"
    
    def get_full_filename(self):
        """Return full filename with path info for type detection."""
        if self.current_file:
            return self.current_file
        return "Untitled"
    
    def get_opacity(self):
        return int(self.root.attributes('-alpha') * 100)
    
    def _about(self):
        messagebox.showinfo("About LiquidPad",
            "LiquidPad v1.0\n\n"
            "A fluid, transparent notepad.\n"
            "7 themes | Glass effects | Find & Replace\n"
            "Live stats | Keyboard shortcuts | Session Recovery\n"
            "Recent Files | Auto-save | Line Numbers\n\n"
            "Built with Python & Tkinter")
    
    def _shortcuts(self):
        messagebox.showinfo("Shortcuts",
            "Ctrl+N  New\n"
            "Ctrl+O  Open\n"
            "Ctrl+S  Save\n"
            "Ctrl+Shift+S  Save As\n"
            "Ctrl+Q  Exit\n\n"
            "Ctrl+Z  Undo\n"
            "Ctrl+Y  Redo\n"
            "Ctrl+X  Cut\n"
            "Ctrl+C  Copy\n"
            "Ctrl+V  Paste\n"
            "Ctrl+A  Select All\n"
            "Ctrl+F  Find & Replace\n\n"
            "Ctrl+Scroll  Zoom In/Out")
