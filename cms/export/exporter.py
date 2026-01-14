"""
Static site exporter for Wagtail.

This module contains the main StaticSiteExporter class that orchestrates
the export of a Wagtail site to standalone HTML.
"""

import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.test import Client
from wagtail.models import Site

from cms.export import ExportError
from cms.export.html_rewriter import HTMLRewriter


class StaticSiteExporter:
    """
    Exports a Wagtail site to static HTML files for offline browsing.
    
    The exporter:
    1. Retrieves all live pages from a Wagtail site
    2. Renders each page to HTML using Django's test client
    3. Rewrites URLs to relative paths
    4. Copies static and media files
    5. Optionally creates a ZIP archive
    """
    
    def __init__(self, site_id_or_hostname, output_dir, exclude_media=False, verbose=False):
        """
        Initialize the exporter.
        
        Args:
            site_id_or_hostname: Site ID (int) or hostname (str)
            output_dir: Path to output directory
            exclude_media: If True, skip copying media files
            verbose: If True, print detailed progress information
        """
        self.site = self._resolve_site(site_id_or_hostname)
        self.output_dir = Path(output_dir)
        self.exclude_media = exclude_media
        self.verbose = verbose
        self.client = Client()
        self.collected_media = set()
        self.pages_exported = 0
        self.pages_failed = 0
    
    def _resolve_site(self, site_id_or_hostname):
        """
        Resolve site from ID or hostname.
        
        Args:
            site_id_or_hostname: Site ID (int/str) or hostname (str)
            
        Returns:
            Site instance
            
        Raises:
            ExportError: If site not found
        """
        try:
            # Try as ID first
            site_id = int(site_id_or_hostname)
            return Site.objects.get(id=site_id)
        except (ValueError, Site.DoesNotExist):
            # Try as hostname
            try:
                return Site.objects.get(hostname=site_id_or_hostname)
            except Site.DoesNotExist:
                raise ExportError(
                    f'Site not found: {site_id_or_hostname}. '
                    f'Available sites: {", ".join(Site.objects.values_list("hostname", flat=True))}'
                )
    
    def export(self):
        """
        Main export orchestration method.
        
        Exports all live pages and assets from the site.
        """
        if self.verbose:
            print(f'Exporting site: {self.site.hostname} (ID: {self.site.id})')
            print(f'Root page: {self.site.root_page}')
        
        # Setup output directory
        self._setup_output_directory()
        
        # Get pages to export
        pages = self._get_pages_to_export()
        if self.verbose:
            print(f'Found {pages.count()} pages to export')
        
        # Export each page
        for page in pages:
            try:
                self._export_page(page)
                self.pages_exported += 1
            except Exception as e:
                self.pages_failed += 1
                if self.verbose:
                    print(f'ERROR exporting {page.url}: {e}')
        
        if self.verbose:
            print(f'Exported {self.pages_exported} pages ({self.pages_failed} failed)')
        
        # Copy static files
        self._copy_static_files()
        
        # Copy media files
        if not self.exclude_media:
            self._copy_media_files()
        elif self.verbose:
            print('Skipping media files (--exclude-media)')
        
        # Create index if needed
        self._create_index_if_needed()
        
        if self.verbose:
            print('Export complete!')
    
    def _setup_output_directory(self):
        """Create output directory if it doesn't exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        if self.verbose:
            print(f'Output directory: {self.output_dir}')
    
    def _get_pages_to_export(self):
        """
        Get all live pages for this site.
        
        Returns:
            QuerySet of Page instances
        """
        root_page = self.site.root_page
        pages = (
            root_page.get_descendants(inclusive=True)
            .live()
            .specific()
            .order_by('path')
        )
        return pages
    
    def _export_page(self, page):
        """
        Export a single page.
        
        Args:
            page: Wagtail Page instance
        """
        if self.verbose:
            print(f'Exporting: {page.url} ({page.title})')
        
        # Calculate output path
        output_path = self._page_to_filepath(page)
        
        # Render HTML
        html = self._render_page(page)
        
        # Calculate page URL relative to site root for rewriter
        # This is needed for correct depth calculation in multi-site setups
        page_url = page.url
        site_root_url = self.site.root_page.url
        
        # Remove site root prefix if present
        if site_root_url != '/' and page_url.startswith(site_root_url):
            page_url_relative = '/' + page_url[len(site_root_url):].lstrip('/')
        else:
            page_url_relative = page_url
        
        # For root page, use just '/'
        if page.id == self.site.root_page.id:
            page_url_relative = '/'
        
        # Rewrite URLs
        rewriter = HTMLRewriter(
            html=html,
            current_page_url=page_url_relative,
            site_root_url='/',  # Always use '/' as site root for rewriter
            output_dir=self.output_dir,
            verbose=self.verbose
        )
        rewritten_html = rewriter.rewrite()
        
        # Track media files
        self.collected_media.update(rewriter.collected_media_files)
        
        # Write to disk
        self._write_html(output_path, rewritten_html)
    
    def _render_page(self, page):
        """
        Render page using Django test client.
        
        Args:
            page: Wagtail Page instance
            
        Returns:
            str: Rendered HTML
            
        Raises:
            ExportError: If rendering fails
        """
        # Get the page URL relative to site root
        # For multi-site setups, page.url may include a site prefix
        # We need to get the URL relative to the site root
        page_url = page.url
        site_root_url = page.get_site().root_page.url
        
        # If page URL starts with site root URL, make it relative
        if site_root_url != '/' and page_url.startswith(site_root_url):
            page_url = '/' + page_url[len(site_root_url):].lstrip('/')
        
        # Set correct HTTP_HOST for multi-domain setup
        response = self.client.get(
            page_url,
            HTTP_HOST=self.site.hostname,
            follow=False
        )
        
        if response.status_code != 200:
            raise ExportError(
                f'Failed to render {page_url} (original: {page.url}): HTTP {response.status_code}'
            )
        
        return response.content.decode('utf-8')
    
    def _page_to_filepath(self, page):
        """
        Convert Wagtail page URL to filesystem path.
        
        Examples:
            / -> index.html
            /proyectos/madmusic/ -> proyectos/madmusic/index.html
            /noticias/evento-2025/ -> noticias/evento-2025/index.html
        
        Args:
            page: Wagtail Page instance
            
        Returns:
            Path: Output file path
        """
        # Check if this is the root page of the site
        if page.id == self.site.root_page.id:
            # Root page goes to index.html
            return self.output_dir / 'index.html'
        
        # Get URL relative to site root
        url_path = page.url.strip('/')
        site_root_url = self.site.root_page.url.strip('/')
        
        # Remove site root prefix if present
        if site_root_url and url_path.startswith(site_root_url):
            url_path = url_path[len(site_root_url):].lstrip('/')
        
        if not url_path:
            # Fallback to root
            return self.output_dir / 'index.html'
        
        # Create directory structure
        page_dir = self.output_dir / url_path
        page_dir.mkdir(parents=True, exist_ok=True)
        
        return page_dir / 'index.html'
    
    def _write_html(self, output_path, html):
        """
        Write HTML content to file.
        
        Args:
            output_path: Path to output file
            html: HTML content string
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _copy_static_files(self):
        """Copy staticfiles to export/static/"""
        static_root = Path(settings.STATIC_ROOT)
        if not static_root.exists():
            raise ExportError(
                'STATIC_ROOT not found. Run "python manage.py collectstatic" first.'
            )
        
        target_dir = self.output_dir / 'static'
        
        if self.verbose:
            print(f'Copying static files from {static_root}...')
        
        # Remove existing static dir if present
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        shutil.copytree(static_root, target_dir)
        
        if self.verbose:
            print(f'Static files copied to {target_dir}')
    
    def _copy_media_files(self):
        """Copy media files referenced in pages"""
        if not hasattr(settings, 'MEDIA_ROOT'):
            # Media is in Azure
            return self._download_azure_media()
        
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            if self.verbose:
                print(f'Warning: MEDIA_ROOT not found: {media_root}')
            return
        
        target_dir = self.output_dir / 'media'
        target_dir.mkdir(exist_ok=True)
        
        if self.verbose:
            print(f'Copying {len(self.collected_media)} media files...')
        
        copied = 0
        for media_path in self.collected_media:
            # Remove /media/ prefix
            rel_path = media_path.replace(settings.MEDIA_URL, '').lstrip('/')
            source_file = media_root / rel_path
            target_file = target_dir / rel_path
            
            if source_file.exists():
                target_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, target_file)
                copied += 1
            elif self.verbose:
                print(f'Warning: Media file not found: {source_file}')
        
        if self.verbose:
            print(f'Copied {copied}/{len(self.collected_media)} media files')
    
    def _download_azure_media(self):
        """Download media from Azure Blob Storage"""
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            raise ExportError(
                'Azure storage not available. Install: pip install azure-storage-blob'
            )
        
        if self.verbose:
            print('Downloading media from Azure Blob Storage...')
        
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={settings.AZURE_ACCOUNT_NAME};"
            f"AccountKey={settings.AZURE_ACCOUNT_KEY};"
            f"EndpointSuffix=core.windows.net"
        )
        
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service.get_container_client(settings.AZURE_CONTAINER)
        
        target_dir = self.output_dir / 'media'
        target_dir.mkdir(exist_ok=True)
        
        downloaded = 0
        for media_url in self.collected_media:
            blob_name = media_url.replace(settings.MEDIA_URL, '').lstrip('/')
            
            try:
                blob_client = container_client.get_blob_client(blob_name)
                target_file = target_dir / blob_name
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(target_file, 'wb') as f:
                    blob_data = blob_client.download_blob()
                    blob_data.readinto(f)
                
                downloaded += 1
            except Exception as e:
                if self.verbose:
                    print(f'Warning: Failed to download {blob_name}: {e}')
        
        if self.verbose:
            print(f'Downloaded {downloaded}/{len(self.collected_media)} media files from Azure')
    
    def _create_index_if_needed(self):
        """
        Create a simple index.html if none exists.
        
        This shouldn't normally be needed as the root page should create it,
        but we include it as a safety measure.
        """
        index_path = self.output_dir / 'index.html'
        if not index_path.exists():
            if self.verbose:
                print('Warning: No index.html found, creating placeholder')
            
            html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Offline Backup</title>
</head>
<body>
    <h1>Offline Backup</h1>
    <p>This is an offline backup of the site. Navigate to the exported pages.</p>
</body>
</html>'''
            self._write_html(index_path, html)
    
    def create_zip(self):
        """
        Create ZIP archive of exported site.
        
        Returns:
            Path: Path to created ZIP file
        """
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        zip_filename = f'offline-backup-{self.site.hostname}-{timestamp}.zip'
        zip_path = self.output_dir.parent / zip_filename
        
        if self.verbose:
            print(f'Creating ZIP archive: {zip_filename}')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in self.output_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.output_dir)
                    zipf.write(file_path, arcname)
        
        if self.verbose:
            size_mb = zip_path.stat().st_size / (1024 * 1024)
            print(f'ZIP created: {zip_path} ({size_mb:.2f} MB)')
        
        return zip_path
