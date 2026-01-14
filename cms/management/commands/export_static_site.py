"""
Management command to export a Wagtail site to static HTML.

This command exports all live pages from a Wagtail site to a standalone
HTML archive that can be browsed offline without a web server.

Usage:
    python manage.py export_static_site --site=1 --output=/tmp/export --zip
    python manage.py export_static_site --site=madmusic --upload-azure --verbose
"""

from django.core.management.base import BaseCommand, CommandError
from cms.export.exporter import StaticSiteExporter
from cms.export.azure_uploader import AzureBackupUploader


class Command(BaseCommand):
    help = 'Export a Wagtail site to static HTML for offline browsing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--site',
            type=str,
            required=True,
            help='Site ID or hostname to export (e.g., "1" or "madmusic.iccmu.es")'
        )
        parser.add_argument(
            '--output',
            type=str,
            default='/tmp/export',
            help='Output directory for the exported site (default: /tmp/export)'
        )
        parser.add_argument(
            '--zip',
            action='store_true',
            help='Create a ZIP archive of the exported site'
        )
        parser.add_argument(
            '--upload-azure',
            action='store_true',
            help='Upload the ZIP to Azure Blob Storage (requires --zip)'
        )
        parser.add_argument(
            '--exclude-media',
            action='store_true',
            help='Skip copying media files (reduces export size)'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output'
        )

    def handle(self, *args, **options):
        try:
            # Validate options
            if options['upload_azure'] and not options['zip']:
                raise CommandError('--upload-azure requires --zip')

            # Create exporter
            exporter = StaticSiteExporter(
                site_id_or_hostname=options['site'],
                output_dir=options['output'],
                exclude_media=options['exclude_media'],
                verbose=options['verbose']
            )

            # Run export
            self.stdout.write(self.style.SUCCESS(
                f'Starting export of site: {options["site"]}'
            ))
            exporter.export()
            self.stdout.write(self.style.SUCCESS(
                f'Export completed to: {options["output"]}'
            ))

            # Create ZIP if requested
            if options['zip']:
                self.stdout.write('Creating ZIP archive...')
                zip_path = exporter.create_zip()
                self.stdout.write(self.style.SUCCESS(
                    f'ZIP created: {zip_path}'
                ))

                # Upload to Azure if requested
                if options['upload_azure']:
                    self.stdout.write('Uploading to Azure Blob Storage...')
                    uploader = AzureBackupUploader()
                    url = uploader.upload(zip_path)
                    self.stdout.write(self.style.SUCCESS(
                        f'Uploaded to Azure: {url}'
                    ))

        except Exception as e:
            raise CommandError(f'Export failed: {str(e)}')
