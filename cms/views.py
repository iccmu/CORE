"""
Views for CMS functionality including backup downloads.
"""

from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import FileResponse, Http404, JsonResponse
from django.views.decorators.http import require_GET

from cms.export.azure_uploader import AzureBackupUploader


@require_GET
@user_passes_test(lambda u: u.is_staff)
def download_offline_backup(request):
    """
    Permite a usuarios staff descargar el backup offline más reciente.
    
    URL: /download-offline-backup/
    
    Requires:
        - User must be authenticated and staff
    
    Returns:
        FileResponse with the latest backup ZIP
    """
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    
    # Create backup directory if it doesn't exist
    backup_dir.mkdir(exist_ok=True)
    
    # Find latest backup
    backups = sorted(backup_dir.glob('offline-backup-*.zip'), reverse=True)
    if not backups:
        raise Http404("No hay backups disponibles")
    
    latest_backup = backups[0]
    
    return FileResponse(
        open(latest_backup, 'rb'),
        as_attachment=True,
        filename=latest_backup.name
    )


@require_GET
def download_offline_backup_signed(request):
    """
    Descarga con token firmado (expira en 1 hora).
    
    URL: /download-offline/?token=<signed_token>
    
    This allows sharing backup downloads without requiring authentication,
    but with time-limited signed tokens for security.
    
    Args:
        request: HttpRequest with 'token' query parameter
    
    Returns:
        FileResponse with the latest backup ZIP
        
    Raises:
        Http404: If token is invalid, expired, or no backups available
    """
    token = request.GET.get('token')
    if not token:
        raise Http404("Token requerido")
    
    signer = TimestampSigner()
    try:
        # Verify token (max age 1 hour = 3600 seconds)
        signer.unsign(token, max_age=3600)
    except (BadSignature, SignatureExpired):
        raise Http404("Token inválido o expirado")
    
    # Token is valid, proceed with download
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    backup_dir.mkdir(exist_ok=True)
    
    # Find latest backup
    backups = sorted(backup_dir.glob('offline-backup-*.zip'), reverse=True)
    if not backups:
        raise Http404("No hay backups disponibles")
    
    latest_backup = backups[0]
    
    return FileResponse(
        open(latest_backup, 'rb'),
        as_attachment=True,
        filename=latest_backup.name
    )


@require_GET
@user_passes_test(lambda u: u.is_staff)
def generate_download_token(request):
    """
    Genera un token firmado para descarga de backup.
    
    URL: /generate-download-token/
    
    Requires:
        - User must be authenticated and staff
    
    Returns:
        JSON with token and download URL
    """
    signer = TimestampSigner()
    token = signer.sign('offline-backup-access')
    
    # Build download URL
    download_url = request.build_absolute_uri('/download-offline/') + f'?token={token}'
    
    return JsonResponse({
        'token': token,
        'download_url': download_url,
        'expires_in_seconds': 3600,
        'expires_in_minutes': 60
    })


@require_GET
@user_passes_test(lambda u: u.is_staff)
def download_from_azure(request):
    """
    Descarga el backup más reciente desde Azure Blob Storage.
    
    URL: /download-from-azure/
    
    Requires:
        - User must be authenticated and staff
        - Azure credentials configured
    
    Returns:
        Redirect to SAS URL for download
    """
    try:
        uploader = AzureBackupUploader()
        
        # Generate SAS URL for latest.zip
        sas_url = uploader.generate_sas_url('latest.zip', expiry_hours=1)
        
        # Return JSON with URL (or redirect)
        return JsonResponse({
            'download_url': sas_url,
            'expires_in_hours': 1
        })
    
    except Exception as e:
        raise Http404(f"Error al acceder a Azure: {str(e)}")


@require_GET
@user_passes_test(lambda u: u.is_staff)
def list_backups(request):
    """
    Lista todos los backups disponibles (local y Azure).
    
    URL: /list-backups/
    
    Requires:
        - User must be authenticated and staff
    
    Returns:
        JSON with list of available backups
    """
    backups = {
        'local': [],
        'azure': []
    }
    
    # List local backups
    backup_dir = Path(settings.BASE_DIR) / 'backups'
    if backup_dir.exists():
        for backup_file in sorted(backup_dir.glob('offline-backup-*.zip'), reverse=True):
            backups['local'].append({
                'name': backup_file.name,
                'size_mb': backup_file.stat().st_size / (1024 * 1024),
                'modified': backup_file.stat().st_mtime
            })
    
    # List Azure backups (if configured)
    if hasattr(settings, 'AZURE_ACCOUNT_NAME') and hasattr(settings, 'AZURE_ACCOUNT_KEY'):
        try:
            uploader = AzureBackupUploader()
            azure_backups = uploader.list_backups()
            backups['azure'] = azure_backups
        except Exception as e:
            backups['azure_error'] = str(e)
    
    return JsonResponse(backups)
