"""
Text editor component for LiquidPadPlus.
Modern full-window design.
"""

import tkinter as tk


class Editor:
    """Main text editing area."""

    def __init__(self, parent, theme):
        self.parent = parent
        self.theme = theme
        self.text_area = None
        self.container = None
        self._font_family = 'JetBrains Mono'
        self._font_size = 12
        self._build()

    def _build(self):
        t = self.theme

        self.container = tk.Frame(self.parent, bg=t["bg"])
        self.container.pack(fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(
            self.container,
            wrap=tk.WORD,
            undo=True,
            maxundo=50,
            bg=t["text_bg"],
            fg=t["fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select_bg"],
            selectforeground=t["fg"],
            relief=tk.FLAT,
            bd=0,
            padx=48,
            pady=36,
            font=(self._font_family, self._font_size),
            highlightthickness=0,
            borderwidth=0,
            spacing1=3,
            spacing2=2,
            spacing3=3
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(
            self.container,
            bg=t["accent"],
            troughcolor=t["text_bg"],
            activebackground=t["border"],
            width=8,
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text_area.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.text_area.yview)
        self.text_area.focus_set()

    def get_text(self):
        return self.text_area.get("1.0", "end-1c")

    def set_text(self, content):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert("1.0", content)

    def clear(self):
        self.text_area.delete("1.0", tk.END)

    def get_stats(self):
        text = self.get_text()
        words = len(text.split()) if text.strip() else 0
        chars = len(text)
        return words, chars

    def set_font_size(self, size):
        """Set font size using cached font family — no cget() call, no lag."""
        self._font_size = size
        self.text_area.configure(font=(self._font_family, size))

    def update_theme(self, theme):
        self.theme = theme
        t = theme
        self.container.configure(bg=t["bg"])
        self.text_area.configure(
            bg=t["text_bg"],
            fg=t["fg"],
            insertbackground=t["cursor"],
            selectbackground=t["select_bg"],
            selectforeground=t["fg"]
        )
