"""
Menu bar component for LiquidPad.
Creates all menus and keyboard shortcuts.
Works with TabManager for multi-file support.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import webbrowser
from findreplace import FindReplace
from exporter import HTMLExporter


class MenuBar:
    """Application menu bar with File, Edit, View, Snippets, and Help menus."""
    
    def __init__(self, root, app, statusbar, theme_callback, focus_callback=None):
        self.root = root
        self.app = app
        self.statusbar = statusbar
        self.change_theme = theme_callback
        self.toggle_focus = focus_callback
        self.themes = {}
        self.current_theme_name = "glass"
        self.find_replace = None
        
    def setup(self, themes, theme_name):
        self.themes = themes
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        self.find_replace = FindReplace(self.root, self.app.tab_manager.get_active_editor())
    
    @property
    def editor(self):
        return self.app.tab_manager.get_active_editor()
    
    @property
    def current_file(self):
        return self.app.tab_manager.get_active_file()
    
    @current_file.setter
    def current_file(self, value):
        self.app.tab_manager.set_active_file(value)
    
    def rebuild(self, theme_name):
        self.current_theme_name = theme_name
        self._create_menus()
        self._bind_keys()
        if self.find_replace:
            self.find_replace.set_theme(self._theme())
            self.find_replace = FindReplace(self.root, self.editor)
    
    def _theme(self):
        return self.themes.get(self.current_theme_name, {
            "bg": "#1a1a2e", "fg": "#ffffff", "accent": "#333333", "text_bg": "#1e1e3a"
        })
    
    def _create_menus(self):
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
        file_menu.add_command(label="New Tab", command=self._new_tab, accelerator="Ctrl+T")
        file_menu.add_command(label="Open", command=self._open, accelerator="Ctrl+O")
        
        self.recent_menu = tk.Menu(file_menu, tearoff=0, bg=t["bg"], fg=t["fg"],
                                    activebackground=t["accent"], activeforeground=t["fg"])
        file_menu.add_cascade(label="Open Recent", menu=self.recent_menu)
        self._build_recent_files_menu()
        
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self._save, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self._save_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="📄 Export as HTML", command=self._export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Close Tab", command=self._close_tab, accelerator="Ctrl+W")
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
        
        if self.toggle_focus:
            view_menu.add_command(label="🎯 Focus Mode", command=self.toggle_focus, accelerator="F11")
        
        if hasattr(self.root, '_app') and hasattr(self.root._app, '_toggle_markdown_preview'):
            view_menu.add_command(
                label="📝 Markdown Preview",
                command=self.root._app._toggle_markdown_preview,
                accelerator="Ctrl+M"
            )
        
        view_menu.add_separator()
        
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
        
        view_menu.add_separator()
        view_menu.add_command(label="Next Tab", command=self._next_tab, accelerator="Ctrl+Tab")
        view_menu.add_command(label="Previous Tab", command=self._prev_tab, accelerator="Ctrl+Shift+Tab")
        
        # === SNIPPETS MENU ===
        snippets_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                               activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Snippets", menu=snippets_menu)
        
        editor = self.editor
        if editor and hasattr(editor, 'snippet_manager'):
            for trigger, preview in editor.snippet_manager.get_snippet_list():
                if len(preview) > 50:
                    preview = preview[:50] + "..."
                display = f"{trigger}  →  {preview}"
                snippets_menu.add_command(
                    label=display,
                    font=('Consolas', 8),
                    state=tk.DISABLED
                )
        
        # === HELP MENU ===
        help_menu = tk.Menu(menubar, tearoff=0, bg=t["bg"], fg=t["fg"],
                           activebackground=t["accent"], activeforeground=t["fg"])
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About LiquidPad", command=self._about)
        help_menu.add_command(label="Shortcuts", command=self._shortcuts)
    
    def _build_recent_files_menu(self):
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
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.app.tab_manager.add_tab(filepath=filepath, content=content)
                self.app.root.title(f"LiquidPad - {os.path.basename(filepath)}")
                
                if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
                    self.root._app.session_manager.add_recent_file(filepath)
                    self._build_recent_files_menu()
                
                self.app._update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file:\n{e}")
        else:
            messagebox.showwarning("File Not Found", 
                f"This file no longer exists:\n{filepath}")
    
    def _clear_recent_files(self):
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
            self.root._app.session_manager.clear_recent_files()
            self._build_recent_files_menu()
    
    def _add_to_recent(self, filepath):
        if not filepath:
            return
        if hasattr(self.root, '_app') and hasattr(self.root._app, 'session_manager'):
            self.root._app.session_manager.add_recent_file(filepath)
            self._build_recent_files_menu()
    
    def _theme_switcher(self, name):
        return lambda: self.change_theme(name)
    
    def _font_switcher(self, size):
        return lambda: self.editor.set_font_size(size) if self.editor else None
    
    def _bind_keys(self):
        self.root.bind('<Control-t>', lambda e: self._new_tab())
        self.root.bind('<Control-n>', lambda e: self._new_tab())
        self.root.bind('<Control-o>', lambda e: self._open())
        self.root.bind('<Control-s>', lambda e: self._save())
        self.root.bind('<Control-S>', lambda e: self._save_as())
        self.root.bind('<Control-w>', lambda e: self._close_tab())
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-f>', lambda e: self._show_find_replace())
        if self.toggle_focus:
            self.root.bind('<F11>', lambda e: self.toggle_focus())
        if hasattr(self.root, '_app') and hasattr(self.root._app, '_toggle_markdown_preview'):
            self.root.bind('<Control-m>', lambda e: self.root._app._toggle_markdown_preview())
    
    def _show_find_replace(self):
        if self.find_replace:
            self.find_replace = FindReplace(self.root, self.editor)
            self.find_replace.set_theme(self._theme())
            self.find_replace.show()
    
    # ---- Actions ----
    
    def _set_opacity(self, value):
        self.root.attributes('-alpha', value)
    
    def _new_tab(self):
        self.app.tab_manager.add_tab()
        self.app._update_status()
    
    def _close_tab(self):
        self.app.tab_manager.close_tab()
        self.app._update_status()
    
    def _next_tab(self):
        self.app.tab_manager.next_tab()
    
    def _prev_tab(self):
        self.app.tab_manager.prev_tab()
    
    def _open(self):
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
                content = f.read()
            self.app.tab_manager.add_tab(filepath=path, content=content)
            self.app.root.title(f"LiquidPad - {os.path.basename(path)}")
            self._add_to_recent(path)
            self.app._update_status()
    
    def _save(self):
        filepath = self.current_file
        editor = self.editor
        if not editor:
            return
        
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(editor.get_text())
            self.app.tab_manager.set_active_modified(False)
            self.app.root.title(f"LiquidPad - {os.path.basename(filepath)}")
            self._add_to_recent(filepath)
            self.app._update_status()
        else:
            self._save_as()
    
    def _save_tab(self, tab):
        if tab['file']:
            with open(tab['file'], 'w', encoding='utf-8') as f:
                f.write(tab['editor'].get_text())
            tab['modified'] = False
        else:
            path = filedialog.asksaveasfilename(
                title="Save As",
                defaultextension=".txt",
                filetypes=[
                    ("All files", "*.*"),
                    ("Python files", "*.py"),
                    ("Text files", "*.txt"),
                ]
            )
            if path:
                tab['file'] = path
                tab['title'] = os.path.basename(path)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(tab['editor'].get_text())
                tab['modified'] = False
    
    def _save_as(self):
        editor = self.editor
        if not editor:
            return
        
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
    
    def _export_html(self):
        """Export current tab as styled HTML and optionally open in browser."""
        editor = self.editor
        if not editor:
            return
        
        content = editor.get_text()
        if not content.strip():
            messagebox.showwarning("LiquidPad", "Nothing to export! Document is empty.")
            return
        
        default_name = "document.html"
        if self.current_file:
            base = os.path.splitext(os.path.basename(self.current_file))[0]
            default_name = f"{base}.html"
        
        path = filedialog.asksaveasfilename(
            title="Export as HTML",
            defaultextension=".html",
            initialfile=default_name,
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if path:
            try:
                title = os.path.basename(path).replace('.html', '')
                theme = self.app.current_theme
                HTMLExporter.export(content, path, theme, title)
                
                if messagebox.askyesno("LiquidPad", 
                    f"✅ Exported successfully!\n\nSaved to:\n{path}\n\nOpen in browser?"):
                    webbrowser.open(path)
                    
            except Exception as e:
                messagebox.showerror("Export Error", f"Could not export:\n{e}")
    
    def _undo(self):
        editor = self.editor
        if editor:
            try: editor.text_area.edit_undo()
            except: pass
    
    def _redo(self):
        editor = self.editor
        if editor:
            try: editor.text_area.edit_redo()
            except: pass
    
    def _cut(self):
        if self.editor:
            self.editor.text_area.event_generate("<<Cut>>")
    
    def _copy(self):
        if self.editor:
            self.editor.text_area.event_generate("<<Copy>>")
    
    def _paste(self):
        if self.editor:
            self.editor.text_area.event_generate("<<Paste>>")
    
    def _select_all(self):
        if self.editor:
            self.editor.text_area.tag_add(tk.SEL, "1.0", tk.END)
            self.editor.text_area.mark_set(tk.INSERT, "1.0")
    
    def get_filename(self):
        return self.app.tab_manager.get_filename()
    
    def get_full_filename(self):
        return self.app.tab_manager.get_full_filename()
    
    def get_opacity(self):
        return int(self.root.attributes('-alpha') * 100)
    
    def _about(self):
        """Show beautiful About dialog."""
        about_window = tk.Toplevel(self.root)
        about_window.title("About LiquidPad")
        about_window.geometry("420x380")
        about_window.configure(bg=self.app.current_theme["bg"])
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        about_window.update_idletasks()
        px = self.root.winfo_rootx()
        py = self.root.winfo_rooty()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        dw = about_window.winfo_width()
        dh = about_window.winfo_height()
        x = px + (pw // 2) - (dw // 2)
        y = py + (ph // 2) - (dh // 2)
        about_window.geometry(f'+{x}+{y}')
        
        t = self.app.current_theme
        
        tk.Label(about_window, text="💧", font=('Segoe UI', 48), bg=t["bg"]).pack(pady=(20, 5))
        tk.Label(about_window, text="LiquidPad", font=('Segoe UI', 20, 'bold'), bg=t["bg"], fg=t.get("cursor", "#ff6b9d")).pack()
        tk.Label(about_window, text="Version 1.0", font=('Segoe UI', 10), bg=t["bg"], fg=t.get("line_fg", "#888888")).pack(pady=(0, 10))
        tk.Frame(about_window, bg=t["accent"], height=1).pack(fill=tk.X, padx=40)
        
        features_frame = tk.Frame(about_window, bg=t["bg"])
        features_frame.pack(pady=(15, 10), padx=30)
        
        for feat in [
            "💎 Glass Effects • 🌈 7 Themes",
            "📏 Line Numbers • 🔍 Find & Replace",
            "💾 Session Recovery • 📄 Recent Files",
            "🎯 Focus Mode • 💬 Snippets",
            "📝 Markdown Preview • 📑 Tabs",
            "🌐 Export HTML • 🖱️ Context Menu",
            "📁 File Type Detection • ⌨️ Shortcuts",
        ]:
            tk.Label(features_frame, text=feat, font=('Segoe UI', 9), bg=t["bg"], fg=t["fg"]).pack(anchor=tk.CENTER, pady=1)
        
        tk.Frame(about_window, bg=t["accent"], height=1).pack(fill=tk.X, padx=40, pady=(5, 10))
        tk.Label(about_window, text="Built with Python & Tkinter\nZero Dependencies • ~25MB RAM", font=('Segoe UI', 8), bg=t["bg"], fg=t.get("line_fg", "#666666"), justify=tk.CENTER).pack()
        
        tk.Button(about_window, text="Close", command=about_window.destroy, bg=t["accent"], fg=t["fg"], relief=tk.FLAT, padx=30, pady=5, font=('Segoe UI', 9), cursor='hand2').pack(pady=(15, 15))
    
    def _shortcuts(self):
        """Show beautiful Shortcuts dialog with working scrollbar."""
        shortcuts_window = tk.Toplevel(self.root)
        shortcuts_window.title("Keyboard Shortcuts")
        shortcuts_window.geometry("500x520")
        shortcuts_window.configure(bg=self.app.current_theme["bg"])
        shortcuts_window.resizable(False, False)
        shortcuts_window.transient(self.root)
        shortcuts_window.grab_set()
        
        shortcuts_window.update_idletasks()
        px = self.root.winfo_rootx()
        py = self.root.winfo_rooty()
        pw = self.root.winfo_width()
        ph = self.root.winfo_height()
        dw = shortcuts_window.winfo_width()
        dh = shortcuts_window.winfo_height()
        x = px + (pw // 2) - (dw // 2)
        y = py + (ph // 2) - (dh // 2)
        shortcuts_window.geometry(f'+{x}+{y}')
        
        t = self.app.current_theme
        
        # Title (outside scrollable area)
        tk.Label(
            shortcuts_window,
            text="⌨️  Keyboard Shortcuts",
            font=('Segoe UI', 16, 'bold'),
            bg=t["bg"],
            fg=t.get("cursor", "#ff6b9d")
        ).pack(pady=(20, 10))
        
        # Scrollable area
        outer_frame = tk.Frame(shortcuts_window, bg=t["bg"])
        outer_frame.pack(fill=tk.BOTH, expand=True, padx=15)
        
        canvas = tk.Canvas(outer_frame, bg=t["bg"], highlightthickness=0, width=460)
        scrollbar = tk.Scrollbar(outer_frame, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=t["bg"])
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Shortcut categories
        categories = {
            "📄 File Operations": [
                ("Ctrl + N / Ctrl + T", "New Tab"),
                ("Ctrl + O", "Open File"),
                ("Ctrl + S", "Save"),
                ("Ctrl + Shift + S", "Save As"),
                ("Ctrl + W", "Close Tab"),
                ("Ctrl + Q", "Exit"),
            ],
            "🔀 Navigation": [
                ("Ctrl + Tab", "Next Tab"),
                ("Ctrl + Shift + Tab", "Previous Tab"),
            ],
            "✏️ Editing": [
                ("Ctrl + Z", "Undo"),
                ("Ctrl + Y", "Redo"),
                ("Ctrl + X", "Cut"),
                ("Ctrl + C", "Copy"),
                ("Ctrl + V", "Paste"),
                ("Ctrl + A", "Select All"),
                ("Ctrl + F", "Find & Replace"),
            ],
            "👁️ View": [
                ("Ctrl + M", "Markdown Preview"),
                ("Ctrl + Scroll", "Zoom In / Out"),
                ("F11", "Focus Mode"),
                ("Esc", "Exit Focus Mode"),
            ],
            "⚡ Other": [
                ("Tab", "Expand Snippet"),
                ("Right Click", "Context Menu"),
            ],
        }
        
        for category, shortcuts in categories.items():
            tk.Label(
                scroll_frame,
                text=category,
                font=('Segoe UI', 11, 'bold'),
                bg=t["bg"],
                fg=t["fg"],
                anchor=tk.W
            ).pack(fill=tk.X, pady=(12, 5), padx=5)
            
            for keys, action in shortcuts:
                row = tk.Frame(scroll_frame, bg=t["bg"])
                row.pack(fill=tk.X, pady=2, padx=5)
                
                tk.Label(
                    row,
                    text=keys,
                    font=('Consolas', 9),
                    bg=t["text_bg"],
                    fg=t.get("cursor", "#ff6b9d"),
                    padx=10,
                    pady=3,
                    width=22,
                    anchor=tk.W
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    row,
                    text=action,
                    font=('Segoe UI', 9),
                    bg=t["bg"],
                    fg=t["fg"],
                    padx=10,
                    anchor=tk.W
                ).pack(side=tk.LEFT)
        
        # Close button (outside scroll)
        tk.Button(
            shortcuts_window,
            text="Close",
            command=shortcuts_window.destroy,
            bg=t["accent"],
            fg=t["fg"],
            relief=tk.FLAT,
            padx=30,
            pady=6,
            font=('Segoe UI', 9),
            cursor='hand2'
        ).pack(pady=(5, 15))