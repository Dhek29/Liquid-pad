"""
Line numbers widget for LiquidPad.
Displays line numbers synced with text editor scroll.
"""

import tkinter as tk


class LineNumbers(tk.Canvas):
    """Line number gutter for text editor."""
    
    def __init__(self, parent, text_widget, theme):
        """
        Initialize line numbers.
        
        Args:
            parent: Parent widget
            text_widget: The Text widget to track
            theme: Theme dictionary with colors
        """
        self.text_widget = text_widget
        self.theme = theme
        
        self.font = ('Cascadia Code', 11)
        self.char_width = 8
        
        super().__init__(
            parent,
            width=40,
            bg=theme.get("line_bg", theme["text_bg"]),
            highlightthickness=0,
            bd=0
        )
        
        self.text_widget.bind('<KeyRelease>', self._update)
        self.text_widget.bind('<MouseWheel>', self._update)
        self.text_widget.bind('<Button-4>', self._update)
        self.text_widget.bind('<Button-5>', self._update)
        self.text_widget.bind('<Configure>', self._update)
        self.text_widget.bind('<Control-Y>', self._schedule_update)
        self.text_widget.bind('<Control-Z>', self._schedule_update)
        
        self._update()
    
    def _schedule_update(self, event=None):
        """Schedule update after event."""
        self.after(10, self._update)
    
    def _update(self, event=None):
        """Redraw line numbers."""
        self.delete("all")
        
        first_line = self.text_widget.index("@0,0")
        first_line_num = int(first_line.split('.')[0])
        
        try:
            last_line = self.text_widget.index(f"@0,{self.text_widget.winfo_height()}")
            last_line_num = int(last_line.split('.')[0])
        except:
            last_line_num = first_line_num + 30
        
        total_lines = int(self.text_widget.index('end-1c').split('.')[0])
        digits = max(3, len(str(total_lines)))
        new_width = digits * self.char_width + 18
        
        if abs(int(self['width']) - new_width) > 5:
            self.configure(width=new_width)
        
        fg_color = self.theme.get("line_fg", self.theme.get("fg", "#888888"))
        
        for line_num in range(first_line_num, last_line_num + 1):
            bbox = self.text_widget.dlineinfo(f"{line_num}.0")
            if bbox:
                y = bbox[1] + bbox[3] // 2
                
                current_line = int(self.text_widget.index(tk.INSERT).split('.')[0])
                if line_num == current_line:
                    fill = self.theme.get("accent", "#444444")
                else:
                    fill = self.theme.get("line_fg", "#666666")
                
                self.create_text(
                    new_width - 10,
                    y,
                    text=str(line_num),
                    anchor=tk.E,
                    font=self.font,
                    fill=fill,
                    tag="line_num"
                )
    
    def update_theme(self, theme):
        """Update colors when theme changes."""
        self.theme = theme
        self.configure(bg=theme.get("line_bg", theme["text_bg"]))
        self._update()
    
    def set_font_size(self, size):
        """Update font size."""
        self.font = ('Cascadia Code', size)
        self._update()