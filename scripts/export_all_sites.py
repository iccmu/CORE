#!/usr/bin/env python
"""
Script de ejemplo para exportar todos los sites de Wagtail programáticamente.

Uso:
    python scripts/export_all_sites.py
    python scripts/export_all_sites.py --upload-azure
    python scripts/export_all_sites.py --exclude-media --verbose
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proyectos.settings')
import django
django.setup()

from wagtail.models import Site
from cms.export.exporter import StaticSiteExporter
from cms.export.azure_uploader import AzureBackupUploader
from cms.export import ExportError


def export_all_sites(output_base='/tmp/exports', upload_azure=False, 
                     exclude_media=False, verbose=False):
    """
    Exporta todos los sites de Wagtail.
    
    Args:
        output_base: Directorio base para exports
        upload_azure: Si True, sube cada ZIP a Azure
        exclude_media: Si True, no copia media files
        verbose: Si True, muestra output detallado
    """
    sites = Site.objects.all()
    
    if verbose:
        print(f"Found {sites.count()} sites to export")
        print("-" * 60)
    
    results = {
        'success': [],
        'failed': []
    }
    
    for site in sites:
        try:
            if verbose:
                print(f"\n{'='*60}")
                print(f"Exporting site: {site.hostname} (ID: {site.id})")
                print(f"{'='*60}")
            
            # Create output directory for this site
            output_dir = Path(output_base) / f"export-{site.hostname}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Export
            exporter = StaticSiteExporter(
                site_id_or_hostname=site.id,
                output_dir=str(output_dir),
                exclude_media=exclude_media,
                verbose=verbose
            )
            exporter.export()
            
            # Create ZIP
            zip_path = exporter.create_zip()
            
            if verbose:
                print(f"\n✅ Export successful: {zip_path}")
            
            # Upload to Azure if requested
            if upload_azure:
                if verbose:
                    print(f"Uploading to Azure...")
                
                uploader = AzureBackupUploader()
                url = uploader.upload(zip_path)
                
                if verbose:
                    print(f"✅ Uploaded to Azure: {url}")
            
            results['success'].append({
                'site': site.hostname,
                'zip_path': str(zip_path),
                'pages_exported': exporter.pages_exported,
                'pages_failed': exporter.pages_failed
            })
        
        except Exception as e:
            if verbose:
                print(f"\n❌ Export failed for {site.hostname}: {e}")
            
            results['failed'].append({
                'site': site.hostname,
                'error': str(e)
            })
    
    return results


def cleanup_old_exports(output_base='/tmp/exports', keep_days=7, verbose=False):
    """
    Limpia exports antiguos.
    
    Args:
        output_base: Directorio base de exports
        keep_days: Días a mantener
        verbose: Si True, muestra output detallado
    """
    import shutil
    from datetime import timedelta
    
    output_path = Path(output_base)
    if not output_path.exists():
        return
    
    cutoff_time = datetime.now() - timedelta(days=keep_days)
    deleted = 0
    
    for export_dir in output_path.glob('export-*'):
        if export_dir.is_dir():
            # Check modification time
            mtime = datetime.fromtimestamp(export_dir.stat().st_mtime)
            if mtime < cutoff_time:
                if verbose:
                    print(f"Deleting old export: {export_dir}")
                shutil.rmtree(export_dir)
                deleted += 1
    
    if verbose and deleted > 0:
        print(f"Cleaned up {deleted} old export(s)")


def print_summary(results):
    """Imprime un resumen de los resultados."""
    print("\n" + "=" * 60)
    print("EXPORT SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ Successful exports: {len(results['success'])}")
    for result in results['success']:
        print(f"  - {result['site']}: {result['pages_exported']} pages exported")
        if result['pages_failed'] > 0:
            print(f"    ⚠️  {result['pages_failed']} pages failed")
    
    if results['failed']:
        print(f"\n❌ Failed exports: {len(results['failed'])}")
        for result in results['failed']:
            print(f"  - {result['site']}: {result['error']}")
    
    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Export all Wagtail sites to static HTML'
    )
    parser.add_argument(
        '--output',
        default='/tmp/exports',
        help='Base output directory (default: /tmp/exports)'
    )
    parser.add_argument(
        '--upload-azure',
        action='store_true',
        help='Upload ZIPs to Azure Blob Storage'
    )
    parser.add_argument(
        '--exclude-media',
        action='store_true',
        help='Skip copying media files'
    )
    parser.add_argument(
        '--cleanup-old',
        type=int,
        metavar='DAYS',
        help='Clean up exports older than N days'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Cleanup old exports if requested
    if args.cleanup_old:
        cleanup_old_exports(
            output_base=args.output,
            keep_days=args.cleanup_old,
            verbose=args.verbose
        )
    
    # Export all sites
    try:
        results = export_all_sites(
            output_base=args.output,
            upload_azure=args.upload_azure,
            exclude_media=args.exclude_media,
            verbose=args.verbose
        )
        
        print_summary(results)
        
        # Exit with error code if any exports failed
        if results['failed']:
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\nExport interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
