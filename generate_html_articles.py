import re
import os

def md_to_html(md_path, html_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    title = 'Article'
    m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if m:
        title = m.group(1)

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset='utf-8'>
<title>{title}</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    max-width: 800px;
    margin: 40px auto;
    padding: 0 24px;
    line-height: 1.8;
    color: #242424;
    background: #fff;
}}
h1 {{ font-size: 38px; line-height: 1.25; margin-bottom: 24px; color: #111; font-weight: 800; }}
h2 {{ font-size: 26px; margin-top: 40px; margin-bottom: 16px; color: #111; font-weight: 700; border-bottom: 1px solid #eee; padding-bottom: 8px; }}
h3 {{ font-size: 20px; margin-top: 28px; margin-bottom: 12px; color: #222; }}
p {{ margin-bottom: 20px; font-size: 18px; }}
code {{ background: #f2f2f2; padding: 2px 6px; border-radius: 4px; font-family: Menlo, Monaco, Consolas, monospace; font-size: 15px; }}
pre {{ background: #1e1e1e; color: #d4d4d4; padding: 18px; border-radius: 8px; overflow-x: auto; font-size: 14px; line-height: 1.5; }}
pre code {{ background: none; color: inherit; padding: 0; }}
blockquote {{ border-left: 3px solid #242424; margin: 0 0 20px 0; padding-left: 20px; color: #555; font-style: italic; }}
img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 24px 0 6px 0; border: 1px solid #e5e5e5; display: block; box-shadow: 0 4px 12px rgba(0,0,0,0.06); }}
.caption {{ color: #666; font-size: 14px; display: block; margin-bottom: 28px; text-align: center; font-style: italic; }}
a {{ color: #1a8917; text-decoration: underline; }}
hr {{ border: none; border-top: 1px solid #eee; margin: 40px 0; }}
ul, ol {{ margin-bottom: 20px; font-size: 18px; padding-left: 28px; }}
li {{ margin-bottom: 8px; }}
.copy-banner {{
    background: #e8f5e9;
    border: 1px solid #c8e6c9;
    padding: 16px 20px;
    border-radius: 8px;
    margin-bottom: 30px;
    font-size: 16px;
    color: #2e7d32;
}}
</style>
</head>
<body>
<div class='copy-banner'>
  💡 <strong>How to publish to Medium in 30 seconds:</strong><br>
  1. Open your draft on Medium.<br>
  2. Press <code>Ctrl + A</code> (Select All) on this page, then <code>Ctrl + C</code> (Copy).<br>
  3. Paste directly into your Medium story. All headings, links, code blocks, and formatted text will paste with 100% fidelity!
</div>
"""
    lines = content.split('\n')
    in_code = False
    code_block = []

    for line in lines:
        if line.startswith('```'):
            if in_code:
                in_code = False
                escaped = '\n'.join(code_block).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                html += f'<pre><code>{escaped}</code></pre>\n'
                code_block = []
            else:
                in_code = True
            continue

        if in_code:
            code_block.append(line)
            continue

        if line.startswith('# '):
            html += f'<h1>{line[2:]}</h1>\n'
        elif line.startswith('## '):
            html += f'<h2>{line[3:]}</h2>\n'
        elif line.startswith('### '):
            html += f'<h3>{line[4:]}</h3>\n'
        elif line.startswith('---'):
            html += '<hr>\n'
        elif line.startswith('> '):
            html += f'<blockquote>{line[2:]}</blockquote>\n'
        elif line.startswith('!['):
            m_img = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if m_img:
                alt, src = m_img.groups()
                # Use absolute local path so it renders directly in browser
                abs_src = os.path.abspath(os.path.join(os.path.dirname(md_path), src))
                html += f'<img src="{abs_src}" alt="{alt}">\n'
        elif line.startswith('*Figure') or line.startswith('*Note'):
            html += f'<span class="caption">{line.strip("*")}</span>\n'
        elif line.startswith('- ') or line.startswith('* '):
            html += f'<ul><li>{line[2:]}</li></ul>\n'
        elif re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line)
            html += f'<ol><li>{text}</li></ol>\n'
        elif line.strip():
            p = line
            p = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', p)
            p = re.sub(r'`(.*?)`', r'<code>\1</code>', p)
            p = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', p)
            p = re.sub(r'\*(.*?)\*', r'<em>\1</em>', p)
            html += f'<p>{p}</p>\n'

    html += '</body></html>'
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'Successfully generated {html_path}')

if __name__ == '__main__':
    md_to_html('d:/hackwithhyd/article_1.md', 'd:/hackwithhyd/article_1.html')
    md_to_html('d:/hackwithhyd/article_2.md', 'd:/hackwithhyd/article_2.html')
