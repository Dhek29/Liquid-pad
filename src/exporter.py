"""
HTML exporter for LiquidPad.
Exports editor content as styled HTML with current theme colors.
"""

import os
import html


class HTMLExporter:
    """Exports text content to styled HTML."""
    
    @staticmethod
    def export(content, filepath, theme, title="LiquidPad Document"):
        """
        Export text as HTML file.
        
        Args:
            content: Text content to export
            filepath: Output file path
            theme: Theme dictionary with colors
            title: HTML page title
        """
        # Escape HTML special characters
        escaped = html.escape(content)
        
        # Convert newlines to <br> and preserve paragraphs
        lines = escaped.split('\n')
        html_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip() == '':
                html_lines.append('<br>')
            else:
                # Wrap in paragraph or div
                html_lines.append(f'<div>{line}</div>')
        
        body_content = '\n'.join(html_lines)
        
        # Build full HTML with theme styling
        html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html.escape(title)}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background-color: {theme["bg"]};
            color: {theme["fg"]};
            font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.8;
            padding: 40px 60px;
            max-width: 900px;
            margin: 0 auto;
            min-height: 100vh;
        }}
        
        div {{
            padding: 2px 0;
        }}
        
        br {{
            content: '';
            display: block;
            margin-bottom: 8px;
        }}
        
        ::selection {{
            background-color: {theme["select_bg"]};
            color: {theme["fg"]};
        }}
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {{
            width: 10px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {theme["text_bg"]};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {theme["accent"]};
            border-radius: 5px;
        }}
        
        /* Footer */
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid {theme["accent"]};
            font-size: 12px;
            color: {theme.get("line_fg", "#666666")};
            text-align: center;
        }}
    </style>
</head>
<body>
{body_content}
    <div class="footer">
        <p>Exported from LiquidPad 💧 | Theme: {theme["name"]}</p>
    </div>
</body>
</html>'''
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        return True