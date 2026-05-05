"""
LiquidPadPlus - Main application class.
Left sidebar + scroll-to-zoom + retractable sidebar.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from themes import THEMES, DEFAULT_THEME
from editor import Editor
from statusbar import StatusBar
from menubar import MenuBar
from sidebar import Sidebar


class LiquidPad:
    """Main LiquidPadPlus application."""

    def __init__(self, root):
        self.root = root
        self.root.title("LiquidPadPlus - Untitled")
        self.root.geometry("950x650")
        self.root.attributes('-alpha', 0.92)
        self.root._app = self

        self._set_icon()

        self.themes = THEMES
        self.current_theme_name = DEFAULT_THEME
        self.current_theme = self.themes[self.current_theme_name]
        self.root.configure(bg=self.current_theme["bg"])

        self.statusbar = None
        self.menubar = None
        self.sidebar = None
        self.editor = None
        self.main_frame = None
        self.editor_frame = None
        self.accent_line = None
        self._built = False
        self._current_font_size = 12
        self._zoom_after_id = None   # for debouncing zoom

        self._build_ui()
        self._center_window()
        self._built = True

        self.root.bind('<KeyRelease>', lambda e: self._safe_update())
        self._bind_scroll_zoom()

    def _set_icon(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', 'icon.ico')
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

    def _build_ui(self):
        t = self.current_theme

        # Status bar first so it anchors to the bottom before main_frame expands
        self.statusbar = StatusBar(self.root, t)

        # Main area
        self.main_frame = tk.Frame(self.root, bg=t["bg"])
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Sidebar — packed first inside main_frame so it always stays left
        callbacks = {
            'new':     self._new_file,
            'open':    self._open_file,
            'save':    self._save_file,
            'save_as': self._save_as_file,
            'cut':     self._cut,
            'copy':    self._copy,
            'paste':   self._paste,
            'find':    self._show_find,
            'themes':  self._show_themes,
            'opacity': self._show_opacity,
            'about':   self._show_about,
        }
        self.sidebar = Sidebar(self.main_frame, t, callbacks)

        # Editor area — fills everything to the right of the sidebar
        self.editor_frame = tk.Frame(self.main_frame, bg=t["bg"])
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.accent_line = tk.Frame(self.editor_frame, bg=t["gradient_start"], height=2)
        self.accent_line.pack(fill=tk.X)

        self.editor = Editor(self.editor_frame, t)

        # Menu bar (built last, references editor)
        self.menubar = MenuBar(self.root, self.editor, self.statusbar, self._change_theme)
        self.menubar.setup(self.themes, self.current_theme_name)

        self._safe_update()

    def _center_window(self):
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - 475
        y = (self.root.winfo_screenheight() // 2) - 325
        self.root.geometry(f'950x650+{x}+{y}')

    def _bind_scroll_zoom(self):
        """Ctrl+Scroll to zoom — debounced so it doesn't lag."""
        def on_scroll(event):
            if event.state & 0x4:
                if event.delta > 0 or event.num == 4:
                    self._current_font_size = min(30, self._current_font_size + 1)
                else:
                    self._current_font_size = max(6, self._current_font_size - 1)

                # Cancel any pending zoom call and schedule a fresh one
                if self._zoom_after_id:
                    self.root.after_cancel(self._zoom_after_id)
                self._zoom_after_id = self.root.after(
                    30, lambda: self.editor.set_font_size(self._current_font_size)
                )

        self.root.bind('<Control-MouseWheel>', on_scroll)
        self.root.bind('<Control-Button-4>', on_scroll)
        self.root.bind('<Control-Button-5>', on_scroll)

    def _change_theme(self, theme_name):
        if not self._built:
            return

        self.current_theme_name = theme_name
        self.current_theme = self.themes[theme_name]
        t = self.current_theme

        # Root and structural frames
        self.root.configure(bg=t["bg"])
        self.main_frame.configure(bg=t["bg"])
        self.editor_frame.configure(bg=t["bg"])
        self.accent_line.configure(bg=t["gradient_start"])

        # Components — all update in-place, no rebuild
        self.statusbar.update_theme(t)
        self.sidebar.update_theme(t)
        self.editor.update_theme(t)
        self.menubar.rebuild(theme_name)

        self._safe_update()

    def _safe_update(self):
        if not self._built or not self.editor:
            return
        try:
            words, chars = self.editor.get_stats()
            fname = self.menubar.get_filename() if self.menubar else "Untitled"
            tname = self.themes.get(self.current_theme_name, {}).get("name", "Unknown")
            opacity = self.menubar.get_opacity() if self.menubar else 92
            self.statusbar.update(fname, words, chars, tname, opacity)
        except tk.TclError:
            pass

    # ── File operations ─────────────────────────────────────────────────────

    def _new_file(self):
        if self.editor.get_text().strip():
            if messagebox.askyesno("New", "Clear current text?"):
                self.editor.clear()
                self.menubar.current_file = None
                self.root.title("LiquidPadPlus - Untitled")
        else:
            self.editor.clear()
            self.menubar.current_file = None
            self.root.title("LiquidPadPlus - Untitled")
        self._safe_update()

    def _open_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            with open(path, 'r', encoding='utf-8') as f:
                self.editor.set_text(f.read())
            self.menubar.current_file = path
            self.root.title(f"LiquidPadPlus - {os.path.basename(path)}")
            self._safe_update()

    def _save_file(self):
        if self.menubar.current_file:
            with open(self.menubar.current_file, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_text())
            self.root.title(f"LiquidPadPlus - {os.path.basename(self.menubar.current_file)}")
        else:
            self._save_as_file()
        self._safe_update()

    def _save_as_file(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            self.menubar.current_file = path
            self._save_file()

    # ── Edit operations ─────────────────────────────────────────────────────

    def _cut(self):
        self.editor.text_area.event_generate("<<Cut>>")

    def _copy(self):
        self.editor.text_area.event_generate("<<Copy>>")

    def _paste(self):
        self.editor.text_area.event_generate("<<Paste>>")

    # ── Popups ──────────────────────────────────────────────────────────────

    def _show_find(self):
        if self.menubar:
            self.menubar._show_find_replace()

    def _show_themes(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Themes")
        popup.geometry("220x340")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 110
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 170
        popup.geometry(f'+{px}+{py}')

        tk.Label(
            popup, text="Choose Theme",
            bg=t["bg"], fg=t["fg"],
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=10)

        for key, data in self.themes.items():
            btn = tk.Label(
                popup,
                text=data["name"],
                bg=t["accent"],
                fg=t["fg"],
                font=('Segoe UI', 9),
                padx=14, pady=6,
                cursor='hand2'
            )
            btn.pack(fill=tk.X, padx=14, pady=1)
            btn.bind('<Button-1>', lambda e, k=key, p=popup: [self._change_theme(k), p.destroy()])

            # Use self.current_theme at hover time so colors are always fresh
            def on_enter(e, b=btn):
                b.configure(bg=self.current_theme["accent_hover"])

            def on_leave(e, b=btn):
                b.configure(bg=self.current_theme["accent"])

            btn.bind('<Enter>', on_enter)
            btn.bind('<Leave>', on_leave)

    def _show_opacity(self):
        t = self.current_theme
        popup = tk.Toplevel(self.root)
        popup.title("Opacity")
        popup.geometry("260x110")
        popup.configure(bg=t["bg"])
        popup.transient(self.root)
        popup.resizable(False, False)

        popup.update_idletasks()
        px = self.root.winfo_rootx() + (self.root.winfo_width() // 2) - 130
        py = self.root.winfo_rooty() + (self.root.winfo_height() // 2) - 55
        popup.geometry(f'+{px}+{py}')

        tk.Label(
            popup, text="Window Opacity",
            bg=t["bg"], fg=t["fg"],
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=(10, 2))

        slider = tk.Scale(
            popup, from_=30, to=100, orient=tk.HORIZONTAL,
            bg=t["bg"], fg=t["fg"], troughcolor=t["accent"],
            highlightthickness=0, length=220, bd=0
        )
        slider.set(int(self.root.attributes('-alpha') * 100))
        slider.pack(pady=4)
        slider.configure(command=lambda v: self.root.attributes('-alpha', float(v) / 100))

    def _show_about(self):
        messagebox.showinfo(
            "About LiquidPadPlus",
            "LiquidPadPlus v1.0\n\n"
            "Modern sidebar notepad.\n"
            "Ctrl+Scroll to zoom\n"
            "Glass effects | Multiple themes\n\n"
            "Built with Python & Tkinter"
        )
