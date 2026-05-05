"""
Visual effects for LiquidPad.
Handles glass morphism, overlays, and transparency effects.
"""

import tkinter as tk


class GlassEffects:
    """Applies glass morphism visual effects to widgets."""
    
    @staticmethod
    def create_glass_color(base_color, lighten_by=30):
        """
        Create a lighter version of a hex color for glass highlights.
        
        Args:
            base_color: Hex color string (e.g., '#ff6b9d')
            lighten_by: Amount to lighten each RGB channel
        
        Returns:
            Lighter hex color string
        """
        r = min(255, int(base_color[1:3], 16) + lighten_by)
        g = min(255, int(base_color[3:5], 16) + lighten_by)
        b = min(255, int(base_color[5:7], 16) + lighten_by)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    @staticmethod
    def add_glass_overlay(parent, theme):
        """
        Add subtle glass-like reflection effects to a frame.
        
        Args:
            parent: Tkinter frame widget
            theme: Theme dictionary with color values
        """
        # Top edge highlight (simulates glass reflection)
        highlight = tk.Frame(
            parent,
            bg=GlassEffects.create_glass_color(theme["text_bg"]),
            height=1,
            bd=0
        )
        highlight.place(relx=0, rely=0, relwidth=1, height=1)
        
        # Left edge highlight
        side_highlight = tk.Frame(
            parent,
            bg=GlassEffects.create_glass_color(theme["text_bg"]),
            width=1,
            bd=0
        )
        side_highlight.place(relx=0, rely=0, width=1, relheight=1)
    
    @staticmethod
    def apply_glass_border(frame, theme):
        """
        Apply glass border effect to a frame.
        
        Args:
            frame: Tkinter frame to style
            theme: Theme dictionary
        """
        if theme.get("glass_effect"):
            border_color = GlassEffects.create_glass_color(theme["border"])
            frame.configure(
                highlightthickness=1,
                highlightbackground=border_color,
                highlightcolor=border_color
            )
        else:
            frame.configure(
                highlightthickness=0
            )
