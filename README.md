# 💧 LiquidPad

**A fluid, transparent notepad with stunning glass effects.**

LiquidPad is a minimalistic, beautiful text editor built with Python and Tkinter. It features adjustable transparency, multiple themes with glass morphism effects, and live writing statistics — all while being incredibly lightweight (~25MB RAM).

![LiquidPad Screenshot](assets/screenshots/glass-theme.png)

---

## ✨ Features

----------------------------------------------------------------------------
🎨 UI & Appearance

🪟 Window Transparency — Adjustable from 50% to 95% opacity

💎 Glass Morphism — Elegant frosted glass effects on selected themes

🌈 7 Beautiful Themes
Glass Dark
Glass Light
Dark
Light
Midnight
Forest
Ocean

🎨 Theme-aware Line Numbers — Colors adapt automatically to match theme

🖼️ Custom App Icon — Styled window and taskbar icon

-----------------------------------------------------------------------------
✍️ Editing Experience

📏 Line Numbers — Synced gutter with current line highlighting

🔍 Find & Replace
Match case
Whole word
Highlight all
Replace all

🖱️ Right-Click Context Menu
Cut / Copy / Paste
Undo / Redo
Select All
Clear Selection

🌐 Web Search — Search selected text instantly on Google

📊 Selection Stats — Shows selected vs total words

-------------------------------------------------------------------------------
⚙️ Productivity Tools

📊 Live Statistics — Real-time word & character count

🔤 Font Control
Adjustable from 8pt to 24pt
Zoom using Ctrl + Scroll

⌨️ Keyboard Shortcuts — Full power-user support

📁 Recent Files — Quick access to last 10 files

---------------------------------------------------------------------------------
💾 File Management

💾 File Operations
New
Open
Save
Save As

📂 Supports All File Types

📁 Smart File Filters — 9 categorized filters in open dialog

📄 File Type Detection
Supports 35+ file types
Icons included (🐍 Python, 🌐 HTML, 🎨 CSS, etc.)

-----------------------------------------------------------------------------------
🔄 Smart Features

💾 Session Recovery
Auto-save every 30 seconds
Restore unsaved work after crash

🔄 Session Memory
Remembers theme
Opacity
Window size & position

🧹 Smart Cleanup
Auto-deletes recovery files after saving

---

## 🚀 Quick Start

LiquidPad/
├── main.py                  # Entry point
├── README.md                # You are here
├── LICENSE                  # MIT License
├── SECURITY.md              # Security policy
├── assets/
│   └── icon.ico             # App icon
├── config/                  # Auto-created
│   ├── liquidpad_config.json
│   └── .liquidpad_recovery.txt
└── src/
    ├── __init__.py          # Version info
    ├── app.py               # Main application
    ├── editor.py            # Text editor widget
    ├── effects.py           # Glass morphism effects
    ├── exporter.py          # HTML export
    ├── findreplace.py       # Find & Replace dialog
    ├── linenumbers.py       # Line number gutter
    ├── markdownview.py      # Markdown preview
    ├── menubar.py           # Menu bar & shortcuts
    ├── session.py           # Auto-save & recovery
    ├── snippets.py          # Text snippets
    ├── statusbar.py         # Status bar & file detection
    ├── tabmanager.py        # Tabbed interface
    └── themes.py            # 7 theme definitions

### Prerequisites
- Python 3.7 or higher (with Tkinter — included by default)

## 📄 License
This project is licensed under the MIT License — see the LICENSE file for details.
