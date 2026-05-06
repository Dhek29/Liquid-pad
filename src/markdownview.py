"""
Markdown preview for LiquidPad.
Renders markdown text into styled HTML-like view.
"""

import tkinter as tk
import re


class MarkdownPreview:
    """Simple Markdown renderer using tkinter Text widget."""
    
    def __init__(self, parent, theme):
        """
        Initialize markdown preview.
        
        Args:
            parent: Parent widget
            theme: Theme dictionary
        """
        self.parent = parent
        self.theme = theme
        self.preview_area = None
        
        self._build()
    
    def _build(self):
        """Build the preview widget."""
        self.preview_area = tk.Text(
            self.parent,
            wrap=tk.WORD,
            bg=self.theme["bg"],
            fg=self.theme["fg"],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=15,
            font=('Segoe UI', 11),
            state=tk.DISABLED,
            highlightthickness=0
        )
        
        # Configure tags for styling
        self.preview_area.tag_configure('h1', font=('Segoe UI', 22, 'bold'), 
                                         spacing1=10, spacing3=10,
                                         foreground=self.theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('h2', font=('Segoe UI', 17, 'bold'), 
                                         spacing1=8, spacing3=8,
                                         foreground=self.theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('h3', font=('Segoe UI', 14, 'bold'), 
                                         spacing1=6, spacing3=6)
        self.preview_area.tag_configure('bold', font=('Segoe UI', 11, 'bold'))
        self.preview_area.tag_configure('italic', font=('Segoe UI', 11, 'italic'))
        self.preview_area.tag_configure('code', font=('Consolas', 10), 
                                         background=self.theme.get("text_bg", "#1e1e3a"),
                                         foreground=self.theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('code_block', font=('Consolas', 10), 
                                         background=self.theme.get("text_bg", "#1e1e3a"),
                                         lmargin1=20, lmargin2=20,
                                         spacing1=5, spacing3=5)
        self.preview_area.tag_configure('list_item', lmargin1=20, lmargin2=35)
        self.preview_area.tag_configure('hr', font=('Segoe UI', 1), 
                                         background=self.theme.get("accent", "#444444"),
                                         spacing1=10, spacing3=10)
        self.preview_area.tag_configure('link', foreground=self.theme.get("cursor", "#58a6ff"),
                                         underline=True)
        self.preview_area.tag_configure('blockquote', lmargin1=25, lmargin2=25,
                                         foreground=self.theme.get("line_fg", "#888888"),
                                         font=('Segoe UI', 11, 'italic'))
    
    def render(self, markdown_text):
        """Render markdown text into preview."""
        self.preview_area.config(state=tk.NORMAL)
        self.preview_area.delete("1.0", tk.END)
        
        lines = markdown_text.split('\n')
        in_code_block = False
        
        for line in lines:
            # Code block
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                if in_code_block:
                    self.preview_area.insert(tk.END, '\n')
                else:
                    self.preview_area.insert(tk.END, '\n')
                continue
            
            if in_code_block:
                self.preview_area.insert(tk.END, line + '\n', 'code_block')
                continue
            
            # Headers
            if line.startswith('# '):
                self.preview_area.insert(tk.END, line[2:] + '\n', 'h1')
            elif line.startswith('## '):
                self.preview_area.insert(tk.END, line[3:] + '\n', 'h2')
            elif line.startswith('### '):
                self.preview_area.insert(tk.END, line[4:] + '\n', 'h3')
            
            # Horizontal rule
            elif line.strip() in ('---', '***', '___'):
                self.preview_area.insert(tk.END, '─' * 50 + '\n', 'hr')
            
            # Blockquote
            elif line.startswith('> '):
                self.preview_area.insert(tk.END, line[2:] + '\n', 'blockquote')
            
            # Unordered list
            elif line.strip().startswith('- ') or line.strip().startswith('* '):
                text = line.strip()[2:]
                self.preview_area.insert(tk.END, '• ' + text + '\n', 'list_item')
            
            # Ordered list
            elif re.match(r'^\d+\.\s', line.strip()):
                text = re.sub(r'^\d+\.\s', '', line.strip())
                num = re.match(r'^\d+', line.strip()).group()
                self.preview_area.insert(tk.END, f'{num}. {text}\n', 'list_item')
            
            # Task list
            elif line.strip().startswith('- [ ]'):
                text = line.strip()[6:]
                self.preview_area.insert(tk.END, '☐ ' + text + '\n', 'list_item')
            elif line.strip().startswith('- [x]') or line.strip().startswith('- [X]'):
                text = line.strip()[6:]
                self.preview_area.insert(tk.END, '☑ ' + text + '\n', 'list_item')
            
            # Empty line
            elif not line.strip():
                self.preview_area.insert(tk.END, '\n')
            
            # Regular text with inline formatting
            else:
                self._insert_formatted_line(line + '\n')
        
        self.preview_area.config(state=tk.DISABLED)
    
    def _insert_formatted_line(self, line):
        """Insert a line with inline formatting (bold, italic, code, links)."""
        # Split by inline code first
        parts = re.split(r'(`[^`]+`)', line)
        
        for part in parts:
            if part.startswith('`') and part.endswith('`'):
                self.preview_area.insert(tk.END, part[1:-1], 'code')
            else:
                self._insert_inline_styles(part)
    
    def _insert_inline_styles(self, text):
        """Insert text with **bold**, *italic*, and [links]()."""
        # Process bold
        segments = re.split(r'(\*\*[^*]+\*\*)', text)
        
        for seg in segments:
            if seg.startswith('**') and seg.endswith('**'):
                self.preview_area.insert(tk.END, seg[2:-2], 'bold')
            else:
                # Process italic
                sub_segments = re.split(r'(\*[^*]+\*)', seg)
                for sub in sub_segments:
                    if sub.startswith('*') and sub.endswith('*') and not sub.startswith('**'):
                        self.preview_area.insert(tk.END, sub[1:-1], 'italic')
                    else:
                        # Process links [text](url)
                        link_parts = re.split(r'(\[([^\]]+)\]\(([^)]+)\))', sub)
                        i = 0
                        while i < len(link_parts):
                            if i + 3 < len(link_parts) and link_parts[i].startswith('['):
                                link_text = link_parts[i+1]
                                link_url = link_parts[i+2]
                                self.preview_area.insert(tk.END, link_text, 'link')
                                i += 4
                            else:
                                if link_parts[i]:
                                    self.preview_area.insert(tk.END, link_parts[i])
                                i += 1
    
    def update_theme(self, theme):
        """Update preview colors."""
        self.theme = theme
        self.preview_area.configure(
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.preview_area.tag_configure('h1', foreground=theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('h2', foreground=theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('code', background=theme.get("text_bg", "#1e1e3a"),
                                         foreground=theme.get("cursor", "#ff6b9d"))
        self.preview_area.tag_configure('code_block', background=theme.get("text_bg", "#1e1e3a"))
        self.preview_area.tag_configure('link', foreground=theme.get("cursor", "#58a6ff"))
        self.preview_area.tag_configure('blockquote', foreground=theme.get("line_fg", "#888888"))
        self.preview_area.tag_configure('hr', background=theme.get("accent", "#444444"))
    
    def pack(self, **kwargs):
        """Pack the preview widget."""
        self.preview_area.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the preview widget."""
        self.preview_area.pack_forget()