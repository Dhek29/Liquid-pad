"""
Text snippets for LiquidPad.
Auto-expands shortcuts into full text.
"""

from datetime import datetime


class SnippetManager:
    """Manages text snippets and expansion."""
    
    def __init__(self):
        """Initialize with default snippets."""
        self.snippets = {
            # Date & Time
            '!date': lambda: datetime.now().strftime('%Y-%m-%d'),
            '!time': lambda: datetime.now().strftime('%H:%M:%S'),
            '!datetime': lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '!year': lambda: datetime.now().strftime('%Y'),
            
            # Code
            '!py': '#!/usr/bin/env python3\n# -*- coding: utf-8 -*-\n',
            '!html': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>Document</title>\n</head>\n<body>\n    \n</body>\n</html>',
            '!jsfunc': 'function name() {\n    \n}',
            '!pyfunc': 'def function_name():\n    """Docstring."""\n    pass',
            '!class': 'class ClassName:\n    """Docstring."""\n    \n    def __init__(self):\n        pass',
            
            # Common
            '!todo': 'TODO: ',
            '!fixme': 'FIXME: ',
            '!note': 'NOTE: ',
            '!hack': 'HACK: ',
            
            # Markdown
            '!mdh1': '# ',
            '!mdh2': '## ',
            '!mdh3': '### ',
            '!mdlink': '[text](url)',
            '!mdimg': '![alt](url)',
            '!mdcode': '```\n\n```',
            '!mdtask': '- [ ] ',
            '!mdtable': '| Column 1 | Column 2 | Column 3 |\n|----------|----------|----------|\n|          |          |          |',
            
            # LiquidPad info
            '!liquidpad': 'Built with LiquidPad 💧',
        }
    
    def expand(self, trigger):
        """
        Expand a snippet trigger.
        
        Args:
            trigger: The trigger text (e.g., '!date')
            
        Returns:
            Expanded text or None if not found
        """
        if trigger in self.snippets:
            snippet = self.snippets[trigger]
            if callable(snippet):
                return snippet()
            return snippet
        return None
    
    def get_all_triggers(self):
        """Get all snippet triggers."""
        return sorted(self.snippets.keys())
    
    def get_snippet_list(self):
        """Get list of (trigger, preview) for display."""
        result = []
        for trigger, snippet in self.snippets.items():
            if callable(snippet):
                preview = snippet()
            else:
                preview = snippet[:40].replace('\n', '↵')
            result.append((trigger, preview))
        return sorted(result)
    
    def add_snippet(self, trigger, text):
        """Add a custom snippet."""
        self.snippets[trigger] = text
    
    def remove_snippet(self, trigger):
        """Remove a snippet."""
        if trigger in self.snippets and not trigger.startswith('!'):
            return
        if trigger in self.snippets:
            del self.snippets[trigger]