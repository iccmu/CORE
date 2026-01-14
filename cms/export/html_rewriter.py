"""
HTML rewriter for static site export.

This module contains the HTMLRewriter class that transforms HTML pages
to use relative URLs instead of absolute URLs, making them suitable for
offline browsing.
"""

import re
from pathlib import Path
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
from django.conf import settings


class HTMLRewriter:
    """
    Reescribe HTML para usar rutas relativas en lugar de absolutas.
    
    Transforma:
        - <a href="/proyectos/madmusic/"> → <a href="../../proyectos/madmusic/index.html">
        - <img src="/media/images/logo.jpg"> → <img src="../../media/images/logo.jpg">
        - <link href="/static/css/style.css"> → <link href="../../static/css/style.css">
    """
    
    def __init__(self, html, current_page_url, site_root_url, output_dir, verbose=False):
        """
        Initialize the rewriter.
        
        Args:
            html: HTML content to rewrite
            current_page_url: URL of the current page (e.g., "/proyectos/madmusic/")
            site_root_url: URL of the site root (e.g., "/")
            output_dir: Path to output directory
            verbose: If True, print detailed information
        """
        self.soup = BeautifulSoup(html, 'html.parser')
        self.current_page_url = current_page_url
        self.site_root_url = site_root_url
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.collected_media_files = set()
    
    def rewrite(self):
        """
        Main rewrite orchestration.
        
        Returns:
            str: Rewritten HTML
        """
        self._rewrite_internal_links()
        self._rewrite_data_urls()
        self._rewrite_media_urls()
        self._rewrite_static_urls()
        self._rewrite_document_urls()
        self._remove_canonical_links()
        self._add_offline_notice()
        
        return str(self.soup)
    
    def _rewrite_internal_links(self):
        """Rewrite <a href> for internal navigation"""
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            
            # Check if it's an absolute URL pointing to localhost (same site)
            if href.startswith('http://127.0.0.1:8000/') or href.startswith('http://localhost:8000/'):
                # Convert to relative path by removing the domain
                href = '/' + href.split('/', 3)[-1] if '/' in href[8:] else '/'
            elif href.startswith('http://') or href.startswith('https://'):
                # Skip external links
                continue
            
            # Skip anchors, admin, etc.
            if self._should_skip_link(href):
                continue
            
            # Remove any /madmusic/ prefix from internal links (multi-site setup)
            if href.startswith('/madmusic/'):
                href = '/' + href[len('/madmusic/'):].lstrip('/')
            
            # Convert to relative path
            relative_path = self._make_relative_page_link(href)
            if relative_path:
                link['href'] = relative_path
    
    def _rewrite_data_urls(self):
        """Rewrite data-url attributes in menu items"""
        for elem in self.soup.find_all(attrs={'data-url': True}):
            data_url = elem['data-url']
            
            # Check if it's an absolute URL pointing to localhost
            if data_url.startswith('http://127.0.0.1:8000/') or data_url.startswith('http://localhost:8000/'):
                # Convert to relative path
                data_url = '/' + data_url.split('/', 3)[-1] if '/' in data_url[8:] else '/'
            elif data_url.startswith('http://') or data_url.startswith('https://'):
                # Skip external URLs
                continue
            
            # Remove /madmusic/ prefix if present
            if data_url.startswith('/madmusic/'):
                data_url = '/' + data_url[len('/madmusic/'):].lstrip('/')
            
            # Convert to relative path
            relative_path = self._make_relative_page_link(data_url)
            if relative_path:
                elem['data-url'] = relative_path
    
    def _rewrite_media_urls(self):
        """Rewrite <img src> and other media references"""
        # Images
        for img in self.soup.find_all('img', src=True):
            src = img['src']
            media_url = getattr(settings, 'MEDIA_URL', '/media/')
            
            if src.startswith('/media/') or src.startswith(media_url):
                relative_src = self._make_relative_media_path(src)
                img['src'] = relative_src
                self.collected_media_files.add(src)
        
        # Background images in style attributes
        for elem in self.soup.find_all(style=True):
            style = elem['style']
            if 'url(' in style and '/media/' in style:
                elem['style'] = self._rewrite_style_urls(style)
    
    def _rewrite_static_urls(self):
        """Rewrite CSS and JS references"""
        static_url = getattr(settings, 'STATIC_URL', '/static/')
        
        # Stylesheets
        for link in self.soup.find_all('link', rel='stylesheet', href=True):
            href = link['href']
            if href.startswith('/static/') or href.startswith(static_url):
                link['href'] = self._make_relative_static_path(href)
        
        # Scripts
        for script in self.soup.find_all('script', src=True):
            src = script['src']
            if src.startswith('/static/') or src.startswith(static_url):
                script['src'] = self._make_relative_static_path(src)
    
    def _rewrite_document_urls(self):
        """Rewrite Wagtail document URLs to direct media paths"""
        for link in self.soup.find_all('a', href=True):
            href = link['href']
            
            # Check for Wagtail document URLs: /documents/123/filename.pdf
            if href.startswith('/documents/'):
                try:
                    # Try to extract document and rewrite to media URL
                    from wagtail.documents.models import Document
                    
                    parts = href.strip('/').split('/')
                    if len(parts) >= 2:
                        doc_id = int(parts[1])
                        doc = Document.objects.get(id=doc_id)
                        
                        # Get the actual file URL
                        file_url = doc.file.url
                        
                        # Rewrite to relative media path
                        relative_path = self._make_relative_media_path(file_url)
                        link['href'] = relative_path
                        self.collected_media_files.add(file_url)
                except (ValueError, Document.DoesNotExist, ImportError):
                    # If we can't resolve, leave as is
                    pass
    
    def _remove_canonical_links(self):
        """Remove canonical links that point to online version"""
        for link in self.soup.find_all('link', rel='canonical'):
            link.decompose()
    
    def _add_offline_notice(self):
        """Add a subtle notice that this is offline version"""
        notice = self.soup.new_tag('div', **{
            'style': (
                'background: #fff3cd; '
                'color: #856404; '
                'padding: 10px; '
                'text-align: center; '
                'font-size: 12px; '
                'border-bottom: 1px solid #ffeaa7;'
            ),
            'class': 'offline-notice'
        })
        notice.string = '📦 Versión offline - Algunas funcionalidades pueden no estar disponibles'
        
        if self.soup.body:
            self.soup.body.insert(0, notice)
    
    def _make_relative_page_link(self, target_url):
        """
        Convert absolute page URL to relative path.
        
        Example:
            Current: /proyectos/madmusic/
            Target: /noticias/evento/
            Output: ../../noticias/evento/index.html
        
        Args:
            target_url: Target URL (absolute path)
            
        Returns:
            str: Relative path or None if unable to convert
        """
        # Normalize URLs
        current_path = self.current_page_url.strip('/')
        target_path = target_url.strip('/')
        
        # Handle root target
        if not target_path:
            current_parts = current_path.split('/') if current_path else []
            up_levels = len(current_parts)
            if up_levels:
                return '/'.join(['..'] * up_levels) + '/index.html'
            else:
                return 'index.html'
        
        # Calculate relative path
        current_parts = current_path.split('/') if current_path else []
        target_parts = target_path.split('/')
        
        # Build relative path
        up_levels = len(current_parts)
        relative_parts = ['..'] * up_levels + target_parts + ['index.html']
        
        return '/'.join(relative_parts)
    
    def _make_relative_media_path(self, media_url):
        """
        Convert /media/... to relative path.
        
        Example:
            Current page: /proyectos/madmusic/ (depth 2)
            Media: /media/images/logo.jpg
            Output: ../../media/images/logo.jpg
        
        Args:
            media_url: Media URL (absolute path)
            
        Returns:
            str: Relative path
        """
        media_url_setting = getattr(settings, 'MEDIA_URL', '/media/')
        
        # Remove /media/ prefix
        if media_url.startswith(media_url_setting):
            media_path = media_url.replace(media_url_setting, '').lstrip('/')
        else:
            media_path = media_url.replace('/media/', '').lstrip('/')
        
        # Calculate depth
        current_path = self.current_page_url.strip('/')
        depth = len(current_path.split('/')) if current_path else 0
        
        # Build relative path
        up_levels = ['..'] * depth
        return '/'.join(up_levels + ['media', media_path])
    
    def _make_relative_static_path(self, static_url):
        """
        Similar to _make_relative_media_path but for static files.
        
        Args:
            static_url: Static URL (absolute path)
            
        Returns:
            str: Relative path
        """
        static_url_setting = getattr(settings, 'STATIC_URL', '/static/')
        
        # Remove /static/ prefix
        if static_url.startswith(static_url_setting):
            static_path = static_url.replace(static_url_setting, '').lstrip('/')
        else:
            static_path = static_url.replace('/static/', '').lstrip('/')
        
        # Calculate depth
        current_path = self.current_page_url.strip('/')
        depth = len(current_path.split('/')) if current_path else 0
        
        # Build relative path
        up_levels = ['..'] * depth
        return '/'.join(up_levels + ['static', static_path])
    
    def _rewrite_style_urls(self, style):
        """
        Rewrite URLs in CSS style attributes.
        
        Example:
            background: url('/media/images/bg.jpg')
            becomes:
            background: url('../../media/images/bg.jpg')
        
        Args:
            style: CSS style string
            
        Returns:
            str: Rewritten style string
        """
        def replace_url(match):
            url = match.group(1).strip('\'"')
            if url.startswith('/media/'):
                relative_url = self._make_relative_media_path(url)
                self.collected_media_files.add(url)
                return f'url({relative_url})'
            elif url.startswith('/static/'):
                relative_url = self._make_relative_static_path(url)
                return f'url({relative_url})'
            return match.group(0)
        
        # Match url(...) in CSS
        pattern = r'url\(([^\)]+)\)'
        return re.sub(pattern, replace_url, style)
    
    def _should_skip_link(self, href):
        """
        Determine if link should not be rewritten.
        
        Args:
            href: Link href attribute
            
        Returns:
            bool: True if link should be skipped
        """
        skip_patterns = [
            '#',  # Anchors
            'http://', 'https://',  # External
            'mailto:', 'tel:',  # Special protocols
            '/admin/', '/wagtail/',  # Wagtail admin
            'javascript:',  # JavaScript
        ]
        return any(href.startswith(pattern) for pattern in skip_patterns)
