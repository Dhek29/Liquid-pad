"""
LiquidPad - Main application class.
Ties together all components: tab manager, statusbar, menubar, themes.
"""

import tkinter as tk
import os
from tkinter import messagebox
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from menubar import MenuBar
from session import SessionManager
from markdownview import MarkdownPreview
from tabmanager import TabManager


class LiquidPad:
    """Main LiquidPad application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPad - Untitled")
        self.root.geometry("900x650")
        self.root.attributes('-alpha', 0.92)
        
        self.root._app = self
        self.focus_mode = False
        self.saved_opacity = 0.92
        self.saved_geometry = ""
        self.markdown_preview = None
        self.show_preview = False
        self._preview_update_job = None
        self.tab_manager = None
        
        self._set_icon()
        
        self.themes = THEMES
        self.current_theme_name = DEFAULT_THEME
        self.current_theme = self.themes[self.current_theme_name]
        
        self.root.configure(bg=self.current_theme["bg"])
        
        self._build_ui()
        self._center_window()
        
        self.root.bind('<KeyRelease>', lambda e: self._update_status())
        self.root.bind('<ButtonRelease-1>', lambda e: self._update_status())
        
        self.setup_session_manager()
    
    def _set_icon(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
        
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except:
                pass
    
    def _build_ui(self):
        self.statusbar = StatusBar(self.root, self.current_theme)
        
        # Tab manager replaces single editor
        self.tab_manager = TabManager(self.root, self)
        
        # For backward compatibility
        self.editor = self.tab_manager.get_active_editor()
        
        self.menubar = MenuBar(self.root, self, self.statusbar, self._change_theme, self._toggle_focus_mode)
        self.menubar.setup(self.themes, self.current_theme_name)
        self._update_status()
    
    @property
    def editor(self):
        """Get current active editor."""
        if self.tab_manager:
            return self.tab_manager.get_active_editor()
        return None
    
    @editor.setter
    def editor(self, value):
        """Set editor (for backward compat)."""
        pass
    
    def _center_window(self):
        self.root.update_idletasks()
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def _change_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]
        self.root.configure(bg=self.current_theme["bg"])
        
        # Update all editors
        for editor in self.tab_manager.get_all_editors():
            editor.update_theme(self.current_theme)
        
        self.statusbar.update_theme(self.current_theme)
        self.tab_manager.update_theme(self.current_theme)
        
        if self.markdown_preview:
            self.markdown_preview.update_theme(self.current_theme)
        
        self.menubar.rebuild(theme_name)
        self._update_status()
    
    def _update_status(self):
        if self.focus_mode:
            return
        
        editor = self.tab_manager.get_active_editor()
        if not editor:
            return
        
        words, chars = editor.get_stats()
        sel_words, sel_chars = editor.get_selection_stats()
        filename = self.tab_manager.get_full_filename()
        theme_name = self.themes[self.current_theme_name]["name"]
        opacity = self.menubar.get_opacity()
        
        self.statusbar.update(filename, words, chars, theme_name, opacity, sel_words, sel_chars)
    
    # ========================
    # FOCUS MODE
    # ========================
    
    def _toggle_focus_mode(self):
        if not self.focus_mode:
            self._enter_focus_mode()
        else:
            self._exit_focus_mode()
    
    def _enter_focus_mode(self):
        self.focus_mode = True
        self.saved_opacity = self.root.attributes('-alpha')
        self.saved_geometry = self.root.geometry()
        
        self.root.config(menu=tk.Menu(self.root))
        self.statusbar.bar.pack_forget()
        self.tab_manager.tab_bar.pack_forget()
        
        editor = self.tab_manager.get_active_editor()
        if editor:
            # Repack with focus-mode padding (wider margins)
            editor.glass_container.pack_forget()
            editor.glass_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
            if editor.line_numbers:
                editor.line_numbers.pack_forget()
            editor.text_area.focus_set()
        
        self.root.attributes('-alpha', 0.96)
        self.root.state('zoomed')
        self.root.configure(bg='#0a0a0a')
        
        self.root.bind('<Escape>', lambda e: self._exit_focus_mode())
        self.root.bind('<F11>', lambda e: self._exit_focus_mode())
        
        current_title = self.root.title()
        self.root.title(f"{current_title} [Focus Mode - Esc to exit]")
    
    def _exit_focus_mode(self):
        self.focus_mode = False
        
        self.menubar._create_menus()
        self.menubar._bind_keys()
        self.statusbar.bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.tab_manager.tab_bar.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        editor = self.tab_manager.get_active_editor()
        if editor:
            # Restore line numbers before repacking
            if editor.line_numbers:
                editor.line_numbers.pack(side=tk.LEFT, fill=tk.Y, before=editor.text_area)
                editor.line_numbers._update()
        
        # Let tab_manager re-assert the correct editor with correct padding.
        # This replaces the manual pack() call that used to conflict.
        active_idx = self.tab_manager._get_active_index()
        self.tab_manager._switch_to_index(active_idx)
        
        self.root.attributes('-alpha', self.saved_opacity)
        self.root.state('normal')
        self.root.geometry(self.saved_geometry)
        self.root.configure(bg=self.current_theme["bg"])
        
        self.root.unbind('<Escape>')
        self.root.unbind('<F11>')
        self.root.bind('<F11>', lambda e: self._toggle_focus_mode())
        
        current_title = self.root.title()
        self.root.title(current_title.replace(" [Focus Mode - Esc to exit]", ""))
        
        editor = self.tab_manager.get_active_editor()
        if editor:
            editor.text_area.focus_set()
        self._update_status()
    
    # ========================
    # MARKDOWN PREVIEW
    # ========================
    
    def _toggle_markdown_preview(self):
        if not self.show_preview:
            self._show_markdown_preview()
        else:
            self._hide_markdown_preview()
    
    def _show_markdown_preview(self):
        if self.focus_mode:
            return
        
        self.show_preview = True
        editor = self.tab_manager.get_active_editor()
        if not editor:
            return
        
        if not self.markdown_preview:
            editor.glass_container.pack_forget()
            editor.glass_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 5), pady=(0, 0))
            
            self.markdown_preview = MarkdownPreview(self.root, self.current_theme)
            self.markdown_preview.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 20), pady=(0, 0))
        
        self.markdown_preview.render(editor.get_text())
        self.root.unbind('<KeyRelease>')
        self.root.bind('<KeyRelease>', self._schedule_preview_update)
    
    def _hide_markdown_preview(self):
        self.show_preview = False
        
        if self.markdown_preview:
            self.markdown_preview.pack_forget()
            self.markdown_preview = None
        
        # Let tab_manager re-assert the correct editor with correct padding
        active_idx = self.tab_manager._get_active_index()
        self.tab_manager._switch_to_index(active_idx)
        
        self.root.unbind('<KeyRelease>')
        self.root.bind('<KeyRelease>', lambda e: self._update_status())
        self.root.bind('<ButtonRelease-1>', lambda e: self._update_status())
    
    def _schedule_preview_update(self, event=None):
        if self._preview_update_job:
            self.root.after_cancel(self._preview_update_job)
        self._preview_update_job = self.root.after(300, self._update_preview)
        self._update_status()
    
    def _update_preview(self):
        if self.markdown_preview and self.show_preview:
            editor = self.tab_manager.get_active_editor()
            if editor:
                self.markdown_preview.render(editor.get_text())
    
    # ========================
    # SESSION RECOVERY
    # ========================
    
    def setup_session_manager(self):
        self.session_manager = SessionManager(self)
    
    def check_session_recovery(self):
        recovery_text = self.session_manager.check_recovery()
        
        if recovery_text:
            restored = messagebox.askyesno(
                "LiquidPad - Session Recovery",
                "⚠️ Unsaved work detected from previous session.\n\n"
                "Would you like to restore it?\n\n"
                "Click 'No' to discard and start fresh."
            )
            
            if restored:
                editor = self.tab_manager.get_active_editor()
                if editor:
                    editor.set_text(recovery_text)
                self.root.title("LiquidPad - [Recovered]")
            else:
                self.session_manager.clear_recovery()
        
        if not self.session_manager.session_loaded:
            state = self.session_manager.load_session_state()
            if state:
                self.session_manager.restore_session(state)
        
        self.session_manager.start_auto_save()
    
    def on_close(self):
        if self.focus_mode:
            self._exit_focus_mode()
        
        self.session_manager.save_session_state()
        
        editor = self.tab_manager.get_active_editor()
        if editor and not editor.get_text().strip():
            self.session_manager.clear_recovery()
        
        self.root.destroy()