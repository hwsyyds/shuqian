#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_nav.py

读取 `infinityBackup.infinity` 并生成一个简单的 HTML 导航页面 `bookmark_nav.html`。

用法:
    python generate_nav.py

输出文件: 与输入文件同目录下的 `bookmark_nav.html`
"""
import json
import os
import re
import sys
import html
from urllib.parse import urlparse
from datetime import datetime


INPUT_FILENAME = 'infinityBackup.infinity'
OUTPUT_FILENAME = 'bookmark_nav.html'


def load_json_with_strip(path):
    """读取文件并剥离 C 风格注释 /* ... */ 再解析为 JSON。"""
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()
    # 移除 /* ... */ 注释块（文件里有 "/* Lines ... omitted */"）
    cleaned = re.sub(r'/\*.*?\*/', '', raw, flags=re.S)
    return json.loads(cleaned)


def normalize_site(item):
    # 提取常见字段，返回统一 dict
    target = item.get('target') or item.get('url') or ''
    display = ''
    try:
        parsed = urlparse(target)
        display = parsed.netloc or target
    except Exception:
        display = target
    return {
        'name': item.get('name') or item.get('title') or item.get('id') or target or '未命名',
        'target': target,
        'display_url': display,
        'bgImage': item.get('bgImage') or item.get('icon') or '',
        'bgType': item.get('bgType') or '',
        'bgColor': item.get('bgColor') or '',
        'bgText': item.get('bgText') or '',
        'type': item.get('type') or 'web',
        'id': item.get('id') or item.get('uuid') or '',
    }


def extract_columns(sites_data):
    """sites_data 是 `data.site.sites`，通常是多列的嵌套列表。
    返回一个列列表，每列是项的列表（site 或 folder）。
    文件夹会保留 children 字段（递归处理）。
    """
    columns = []
    for col in sites_data:
        col_items = []
        for item in col:
            if not isinstance(item, dict):
                continue
            if 'children' in item and isinstance(item.get('children'), list):
                # folder
                children = []
                for c in item.get('children'):
                    if not isinstance(c, dict):
                        continue
                    if c.get('type') == 'web' or c.get('target'):
                        children.append(normalize_site(c))
                col_items.append({'kind': 'folder', 'name': item.get('name') or '文件夹', 'children': children})
            else:
                # 单个站点
                if item.get('type') == 'web' or item.get('target'):
                    col_items.append({'kind': 'site', **normalize_site(item)})
        columns.append(col_items)
    return columns


def render_html(columns, title='书签导航'):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 明亮、简约的 CSS 主题（更明亮、强调色彩）
        css = '''
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3a0ca3;
            --light-color: #f8f9fa;
            --dark-color: #212529;
            --gray-color: #6c757d;
            --border-color: #e9ecef;
            --card-bg: white;
            --hover-bg: #f8f9fa;
            --transition: all 0.2s ease;
        }
        
        body {
            background-color: #f8f9fa;
            color: var(--dark-color);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px 0;
            text-align: center;
            margin-bottom: 40px;
        }
        
        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }
        
        .logo i {
            font-size: 2.5rem;
            margin-right: 15px;
        }
        
        .logo h1 {
            font-size: 2.2rem;
            font-weight: 700;
        }
        
        .tagline {
            font-size: 1.1rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .search-container {
            max-width: 700px;
            margin: 0 auto 40px;
        }
        
        .search-box {
            display: flex;
            background: white;
            border-radius: 50px;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        
        .search-box input {
            flex: 1;
            border: none;
            padding: 18px 25px;
            font-size: 1rem;
            outline: none;
        }
        
        .search-box button {
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 0 30px;
            cursor: pointer;
            font-size: 1.1rem;
            transition: var(--transition);
        }
        
        .search-box button:hover {
            background-color: var(--secondary-color);
        }
        
        .category {
            background: var(--card-bg);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .category h2 {
            display: flex;
            align-items: center;
            font-size: 1.4rem;
            margin-bottom: 20px;
            color: var(--dark-color);
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border-color);
        }
        
        .category h2 i {
            margin-right: 10px;
            color: var(--primary-color);
        }
        
        .sites-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
        }
        
        .site-item {
            display: flex;
            align-items: center;
            padding: 15px;
            background: var(--card-bg);
            border-radius: 12px;
            transition: var(--transition);
            text-decoration: none;
            color: var(--dark-color);
            border: 1px solid var(--border-color);
        }
        
        .site-item:hover {
            transform: translateY(-2px);
            background: var(--hover-bg);
        }
        
        .site-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: white;
            border-radius: 8px;
            margin-right: 15px;
            font-size: 1.2rem;
            color: var(--primary-color);
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            overflow: hidden;
            border: 1px solid var(--border-color);
        }
        .site-icon > i {
            position: relative;
            z-index: 1;
        }
        
        .site-info h3 {
            font-size: 1rem;
            margin-bottom: 3px;
        }
        
        .site-info p {
            font-size: 0.85rem;
            color: var(--gray-color);
        }
        
        footer {
            background: var(--dark-color);
            color: white;
            padding: 30px 0;
            text-align: center;
            margin-top: 50px;
        }
        
        .footer-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        
        .copyright {
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 10px;
        }
        
        @media (max-width: 768px) {
            .sites-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            }
        }
        '''

        def esc(s):
            return html.escape(s or '')

        # Enhanced URL escaping for CSS
        def esc_css_url(url):
            if not url:
                return ''
            # Escape single quotes and other special characters for CSS URLs
            escaped = url.replace("'", "\\'")
            return f"'{escaped}'"

        parts = []
        parts.append(f'<!doctype html>\n<html lang="zh-CN">\n<head>\n<meta charset="utf-8">')
        parts.append(f'<meta name="viewport" content="width=device-width,initial-scale=1">')
        parts.append(f'<title>{esc(title)}</title>')
        parts.append(f'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">')
        parts.append(f'<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">')
        parts.append(f'<style>{css}</style>')
        parts.append('</head>\n<body>')
        
        # Header section with logo and tagline
        parts.append(f'<header>')
        parts.append(f'    <div class="container">')
        parts.append(f'        <div class="logo">')
        parts.append(f'            <i class="fas fa-bookmark"></i>')
        parts.append(f'            <h1>{esc(title)}</h1>')
        parts.append(f'        </div>')
        parts.append(f'        <p class="tagline">无敌暴龙神的书签，简洁高效的上网入口</p>')
        parts.append(f'    </div>')
        parts.append(f'</header>')
        
        # Main content
        parts.append(f'<main class="container">')
        parts.append(f'    <div class="search-container">')
        parts.append(f'        <div class="search-box">')
        parts.append(f'            <input type="text" id="site-search" placeholder="输入关键词搜索书签...">')
        parts.append(f'            <button><i class="fas fa-search"></i></button>')
        parts.append(f'        </div>')
        parts.append(f'    </div>')
        
        # Collect all folders from all columns
        all_folders = []
        for col in columns:
            for item in col:
                if item.get('kind') == 'folder':
                    all_folders.append(item)
            
        # Generate category sections
        for folder in all_folders:
            folder_name = esc(folder.get('name'))
            parts.append(f'<div class="category">')
            parts.append(f'<h2><i class="fas fa-folder"></i> {folder_name}</h2>')
            parts.append('<div class="sites-grid">')
            
            # Generate site items with improved icon handling
            for site in folder.get('children', []):
                name = esc(site.get('name'))
                target = site.get('target') or ''
                display = esc(site.get('display_url') or '')
                bg = site.get('bgImage') or ''
                
                # Extract domain for favicon fallback
                domain = ''
                if target:
                    try:
                        domain = urlparse(target).netloc
                    except:
                        pass
                
                parts.append(f'<a class="site-item" href="{html.escape(target)}" target="_blank" rel="noopener noreferrer" title="{html.escape(target)}">')
                if bg:
                    # Use background image with proper CSS escaping
                    css_url = esc_css_url(bg)
                    parts.append(f'<div class="site-icon" style="background-image: url({css_url})"></div>')
                else:
                    # Fallback to domain-based icon
                    if domain:
                        parts.append(f'<div class="site-icon"><i class="fas fa-globe"></i></div>')
                    else:
                        parts.append(f'<div class="site-icon"><i class="fas fa-link"></i></div>')
                parts.append('<div class="site-info">')
                parts.append(f'<h3>{name}</h3>')
                parts.append(f'<p>{display}</p>')
                parts.append('</div>')
                parts.append('</a>')
            
            parts.append('</div>')
            parts.append('</div>')
        
        # Handle standalone sites (not in folders)
        standalone_sites = []
        for col in columns:
            for item in col:
                if item.get('kind') == 'site':
                    standalone_sites.append(item)
            
        if standalone_sites:
            parts.append('<div class="category">')
            parts.append('<h2><i class="fas fa-globe"></i> 未分类书签</h2>')
            parts.append('<div class="sites-grid">')
            
            for site in standalone_sites:
                name = esc(site.get('name'))
                target = site.get('target') or ''
                display = esc(site.get('display_url') or '')
                bg = site.get('bgImage') or ''
                style_bg = f'background-image:url({html.escape(bg)});' if bg else ''
                
                parts.append(f'<a class="site-item" href="{html.escape(target)}" target="_blank" rel="noopener noreferrer" title="{html.escape(target)}">')
                if bg:
                    parts.append(f'<div class="site-icon" style="{style_bg}"></div>')
                else:
                    parts.append(f'<div class="site-icon"><i class="fas fa-link"></i></div>')
                parts.append('<div class="site-info">')
                parts.append(f'<h3>{name}</h3>')
                parts.append(f'<p>{display}</p>')
                parts.append('</div>')
                parts.append('</a>')
            
            parts.append('</div>')
            parts.append('</div>')
        
        parts.append('</main>')
        
        # Footer section
        parts.append(f'<footer>')
        parts.append(f'    <div class="container">')
        parts.append(f'        <div class="footer-content">')
        parts.append(f'            <div class="logo">')
        parts.append(f'                <i class="fas fa-bookmark"></i>')
        parts.append(f'                <h2>{esc(title)}</h2>')
        parts.append(f'            </div>')
        parts.append(f'            <p class="copyright">© {datetime.now().strftime('%Y')} {esc(title)}. 本页面由脚本自动生成.</p>')
        parts.append(f'        </div>')
        parts.append(f'    </div>')
        parts.append(f'</footer>')
        
        # JavaScript: search functionality
        script = '''
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            const searchInput = document.getElementById('site-search');
            const siteItems = document.querySelectorAll('.site-item');
            
            // Search functionality
            searchInput.addEventListener('input', function(e) {
                const query = e.target.value.trim().toLowerCase();
                
                siteItems.forEach(item => {
                    const name = item.querySelector('.site-info h3').textContent.toLowerCase();
                    const url = item.querySelector('.site-info p').textContent.toLowerCase();
                    
                    if (name.includes(query) || url.includes(query)) {
                        item.style.display = 'flex';
                    } else {
                        item.style.display = 'none';
                    }
                });

                // Update category visibility
                document.querySelectorAll('.category').forEach(category => {
                    const visibleItems = Array.from(category.querySelectorAll('.site-item'))
                        .filter(item => item.style.display !== 'none');
                    category.style.display = visibleItems.length > 0 ? 'block' : 'none';
                });
            });
            
            // Add hover effects to categories
            const categories = document.querySelectorAll('.category');
            categories.forEach(category => {
                category.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                    this.style.transition = 'transform 0.3s ease';
                });
                
                category.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
        </script>
        '''
        
        parts.append(script)
        parts.append('</body>')
        parts.append('</html>')
        return '\n'.join(parts)


def main():
    try:
        # Load and parse JSON data
        json_data = load_json_with_strip(INPUT_FILENAME)
        
        # Extract sites data from correct path in JSON structure
        sites_data = json_data.get('data', {}).get('site', {}).get('sites', [])
        
        # Check if we found valid data
        if not sites_data:
            print('⚠️ 未找到有效的书签数据，请检查infinityBackup.infinity文件结构')
            return
            
        # Extract columns from sites data
        columns = extract_columns(sites_data)
        html = render_html(columns)
        output_path = os.path.join(os.getcwd(), 'bookmarks.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'✅ 书签导航页面已成功生成: {os.path.abspath(output_path)}')
        print(f'请打开该文件查看效果')
    except Exception as e:
        print(f'❌ 生成书签页面时出错: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
