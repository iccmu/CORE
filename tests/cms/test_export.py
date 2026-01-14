"""
Tests for static site export functionality.
"""

import tempfile
import zipfile
from pathlib import Path

from django.test import TestCase, Client
from django.contrib.auth.models import User
from wagtail.models import Site, Page
from wagtail.test.utils import WagtailPageTests

from cms.models import HomePage, StandardPage
from cms.export.exporter import StaticSiteExporter
from cms.export.html_rewriter import HTMLRewriter
from cms.export import ExportError


class StaticSiteExporterTestCase(WagtailPageTests):
    """Tests for StaticSiteExporter class"""
    
    def setUp(self):
        """Set up test data"""
        # Get the default site and root page
        self.site = Site.objects.get(is_default_site=True)
        self.root_page = self.site.root_page
        
        # Create a HomePage
        self.home_page = HomePage(
            title="Test Home",
            slug="test-home",
            intro="Test intro"
        )
        self.root_page.add_child(instance=self.home_page)
        
        # Create some StandardPages
        self.page1 = StandardPage(
            title="Page 1",
            slug="page-1",
            intro="Intro for page 1"
        )
        self.home_page.add_child(instance=self.page1)
        
        self.page2 = StandardPage(
            title="Page 2",
            slug="page-2",
            intro="Intro for page 2"
        )
        self.home_page.add_child(instance=self.page2)
        
        # Create a nested page
        self.nested_page = StandardPage(
            title="Nested Page",
            slug="nested",
            intro="Nested page intro"
        )
        self.page1.add_child(instance=self.nested_page)
        
        # Update the site root to the home page
        self.site.root_page = self.home_page
        self.site.save()
    
    def test_resolve_site_by_id(self):
        """Test that site can be resolved by ID"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = StaticSiteExporter(
                site_id_or_hostname=str(self.site.id),
                output_dir=tmpdir
            )
            self.assertEqual(exporter.site, self.site)
    
    def test_resolve_site_by_hostname(self):
        """Test that site can be resolved by hostname"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = StaticSiteExporter(
                site_id_or_hostname=self.site.hostname,
                output_dir=tmpdir
            )
            self.assertEqual(exporter.site, self.site)
    
    def test_resolve_site_invalid(self):
        """Test that invalid site raises error"""
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ExportError):
                StaticSiteExporter(
                    site_id_or_hostname='invalid-site',
                    output_dir=tmpdir
                )
    
    def test_get_pages_to_export(self):
        """Test that all live pages are retrieved"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = StaticSiteExporter(
                site_id_or_hostname=self.site.id,
                output_dir=tmpdir
            )
            pages = exporter._get_pages_to_export()
            
            # Should include home page and all children
            self.assertGreaterEqual(pages.count(), 4)  # home, page1, page2, nested
    
    def test_page_to_filepath(self):
        """Test URL to filepath conversion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = StaticSiteExporter(
                site_id_or_hostname=self.site.id,
                output_dir=tmpdir
            )
            
            # Root page
            self.home_page.url = '/'
            filepath = exporter._page_to_filepath(self.home_page)
            self.assertEqual(filepath, Path(tmpdir) / 'index.html')
            
            # Regular page
            self.page1.url = '/page-1/'
            filepath = exporter._page_to_filepath(self.page1)
            self.assertEqual(filepath, Path(tmpdir) / 'page-1' / 'index.html')
            
            # Nested page
            self.nested_page.url = '/page-1/nested/'
            filepath = exporter._page_to_filepath(self.nested_page)
            self.assertEqual(filepath, Path(tmpdir) / 'page-1' / 'nested' / 'index.html')
    
    def test_export_creates_files(self):
        """Test that export creates HTML files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = StaticSiteExporter(
                site_id_or_hostname=self.site.id,
                output_dir=tmpdir,
                exclude_media=True  # Skip media for faster test
            )
            
            # Note: This may fail if STATIC_ROOT doesn't exist
            # In that case, the test will be skipped
            try:
                exporter.export()
                
                # Check that index.html was created
                self.assertTrue((Path(tmpdir) / 'index.html').exists())
                
                # Check pages exported count
                self.assertGreater(exporter.pages_exported, 0)
            except ExportError as e:
                if 'STATIC_ROOT not found' in str(e):
                    self.skipTest('STATIC_ROOT not found, run collectstatic first')
                else:
                    raise
    
    def test_create_zip(self):
        """Test ZIP creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple export structure
            output_dir = Path(tmpdir) / 'export'
            output_dir.mkdir()
            
            # Create a test file
            (output_dir / 'index.html').write_text('<html><body>Test</body></html>')
            
            exporter = StaticSiteExporter(
                site_id_or_hostname=self.site.id,
                output_dir=str(output_dir)
            )
            
            zip_path = exporter.create_zip()
            
            # Verify ZIP was created
            self.assertTrue(zip_path.exists())
            
            # Verify ZIP contains the file
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                names = zipf.namelist()
                self.assertIn('index.html', names)


class HTMLRewriterTestCase(TestCase):
    """Tests for HTMLRewriter class"""
    
    def test_rewrite_internal_links(self):
        """Test that internal links are rewritten to relative paths"""
        html = '''
        <html>
        <body>
            <a href="/">Home</a>
            <a href="/page-1/">Page 1</a>
            <a href="/page-2/">Page 2</a>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Check that links are relative
            self.assertIn('href="index.html"', rewritten)
            self.assertIn('href="page-1/index.html"', rewritten)
            self.assertIn('href="page-2/index.html"', rewritten)
    
    def test_rewrite_nested_page_links(self):
        """Test link rewriting from a nested page"""
        html = '''
        <html>
        <body>
            <a href="/">Home</a>
            <a href="/page-1/">Page 1</a>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/page-1/nested/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Check that links go up correctly
            self.assertIn('href="../../index.html"', rewritten)
            self.assertIn('href="../index.html"', rewritten)
    
    def test_skip_external_links(self):
        """Test that external links are not rewritten"""
        html = '''
        <html>
        <body>
            <a href="https://example.com">External</a>
            <a href="http://example.com">External HTTP</a>
            <a href="mailto:test@example.com">Email</a>
            <a href="#anchor">Anchor</a>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # External links should remain unchanged
            self.assertIn('href="https://example.com"', rewritten)
            self.assertIn('href="http://example.com"', rewritten)
            self.assertIn('href="mailto:test@example.com"', rewritten)
            self.assertIn('href="#anchor"', rewritten)
    
    def test_rewrite_media_urls(self):
        """Test that media URLs are rewritten"""
        html = '''
        <html>
        <body>
            <img src="/media/images/logo.jpg" alt="Logo">
            <img src="/media/documents/file.pdf" alt="Doc">
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Media paths should be relative
            self.assertIn('src="media/images/logo.jpg"', rewritten)
            self.assertIn('src="media/documents/file.pdf"', rewritten)
            
            # Check that media files were collected
            self.assertEqual(len(rewriter.collected_media_files), 2)
    
    def test_rewrite_media_urls_nested_page(self):
        """Test media URL rewriting from nested page"""
        html = '''
        <html>
        <body>
            <img src="/media/images/logo.jpg" alt="Logo">
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/page-1/nested/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Media path should go up two levels
            self.assertIn('src="../../media/images/logo.jpg"', rewritten)
    
    def test_rewrite_static_urls(self):
        """Test that static URLs are rewritten"""
        html = '''
        <html>
        <head>
            <link rel="stylesheet" href="/static/css/style.css">
            <script src="/static/js/script.js"></script>
        </head>
        <body>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Static paths should be relative
            self.assertIn('href="static/css/style.css"', rewritten)
            self.assertIn('src="static/js/script.js"', rewritten)
    
    def test_remove_canonical_links(self):
        """Test that canonical links are removed"""
        html = '''
        <html>
        <head>
            <link rel="canonical" href="https://example.com/page/">
        </head>
        <body>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Canonical link should be removed
            self.assertNotIn('rel="canonical"', rewritten)
    
    def test_add_offline_notice(self):
        """Test that offline notice is added"""
        html = '''
        <html>
        <body>
            <h1>Test Page</h1>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # Offline notice should be present
            self.assertIn('Versión offline', rewritten)
            self.assertIn('offline-notice', rewritten)
    
    def test_rewrite_style_urls(self):
        """Test URL rewriting in style attributes"""
        html = '''
        <html>
        <body>
            <div style="background: url('/media/images/bg.jpg')">Content</div>
        </body>
        </html>
        '''
        
        with tempfile.TemporaryDirectory() as tmpdir:
            rewriter = HTMLRewriter(
                html=html,
                current_page_url='/',
                site_root_url='/',
                output_dir=tmpdir
            )
            rewritten = rewriter.rewrite()
            
            # URL in style should be rewritten
            self.assertIn('url(media/images/bg.jpg)', rewritten)


class DownloadViewsTestCase(TestCase):
    """Tests for backup download views"""
    
    def setUp(self):
        """Set up test user"""
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='regular',
            password='testpass123',
            is_staff=False
        )
    
    def test_download_offline_backup_requires_staff(self):
        """Test that download view requires staff permission"""
        response = self.client.get('/download-offline-backup/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Regular user should also be denied
        self.client.login(username='regular', password='testpass123')
        response = self.client.get('/download-offline-backup/')
        self.assertEqual(response.status_code, 302)
    
    def test_generate_download_token_requires_staff(self):
        """Test that token generation requires staff permission"""
        response = self.client.get('/generate-download-token/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_generate_download_token_staff(self):
        """Test that staff can generate download tokens"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get('/generate-download-token/')
        self.assertEqual(response.status_code, 200)
        
        # Should return JSON with token
        data = response.json()
        self.assertIn('token', data)
        self.assertIn('download_url', data)
        self.assertIn('expires_in_seconds', data)
    
    def test_list_backups_requires_staff(self):
        """Test that listing backups requires staff permission"""
        response = self.client.get('/list-backups/')
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
    
    def test_list_backups_staff(self):
        """Test that staff can list backups"""
        self.client.login(username='staff', password='testpass123')
        response = self.client.get('/list-backups/')
        self.assertEqual(response.status_code, 200)
        
        # Should return JSON with local and azure keys
        data = response.json()
        self.assertIn('local', data)
        self.assertIn('azure', data)
