"""
Theme definitions for LiquidPad.
Each theme is a dictionary with color values.
To add a new theme, just copy an existing one and modify the colors.
"""

THEMES = {
    "glass": {
        "name": "💎 Glass Dark",
        "glass_effect": True,
        "bg": "#1a1a2e",
        "text_bg": "#1e1e3a",
        "fg": "#e8e8f0",
        "cursor": "#ff6b9d",
        "select_bg": "#3d2d5e",
        "accent": "#1a1a3e",
        "border": "#ff6b9d"
    },
    
    "glass_light": {
        "name": "💎 Glass Light",
        "glass_effect": True,
        "bg": "#e8e8f0",
        "text_bg": "#f5f5ff",
        "fg": "#2d2d3e",
        "cursor": "#ff4081",
        "select_bg": "#d0c4e8",
        "accent": "#dcdce8",
        "border": "#ff4081"
    },
    
    "dark": {
        "name": "🌙 Dark",
        "glass_effect": False,
        "bg": "#1a1a2e",
        "text_bg": "#16213e",
        "fg": "#e0e0e0",
        "cursor": "#e94560",
        "select_bg": "#533483",
        "accent": "#0f3460",
        "border": "#e94560"
    },
    
    "light": {
        "name": "☀️ Light",
        "glass_effect": False,
        "bg": "#f0f0f0",
        "text_bg": "#ffffff",
        "fg": "#333333",
        "cursor": "#2196F3",
        "select_bg": "#BBDEFB",
        "accent": "#e0e0e0",
        "border": "#2196F3"
    },
    
    "midnight": {
        "name": "🌑 Midnight",
        "glass_effect": False,
        "bg": "#0d1117",
        "text_bg": "#161b22",
        "fg": "#c9d1d9",
        "cursor": "#58a6ff",
        "select_bg": "#264f78",
        "accent": "#21262d",
        "border": "#58a6ff"
    },
    
    "forest": {
        "name": "🌲 Forest",
        "glass_effect": False,
        "bg": "#1b2a1b",
        "text_bg": "#243324",
        "fg": "#d4e6d4",
        "cursor": "#4caf50",
        "select_bg": "#2d442d",
        "accent": "#2d442d",
        "border": "#4caf50"
    },
    
    "ocean": {
        "name": "🌊 Ocean",
        "glass_effect": False,
        "bg": "#1a2332",
        "text_bg": "#243447",
        "fg": "#bbdefb",
        "cursor": "#64b5f6",
        "select_bg": "#1e3a5f",
        "accent": "#1e3a5f",
        "border": "#64b5f6"
    }
}

# Default theme when app starts
DEFAULT_THEME = "glass"