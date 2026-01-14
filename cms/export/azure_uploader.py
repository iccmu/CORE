"""
Azure Blob Storage uploader for static site backups.

This module handles uploading ZIP archives to Azure Blob Storage
for long-term backup storage.
"""

from pathlib import Path

from django.conf import settings

from cms.export import ExportError


class AzureBackupUploader:
    """
    Upload backup ZIP to Azure Blob Storage.
    
    Uploads backups to a container in Azure Blob Storage and maintains
    a "latest.zip" file for easy access to the most recent backup.
    """
    
    def __init__(self, container_name='backups'):
        """
        Initialize the uploader.
        
        Args:
            container_name: Name of Azure container to upload to
        """
        self.container_name = container_name
        self.blob_service = self._get_blob_service()
    
    def _get_blob_service(self):
        """
        Create and return BlobServiceClient.
        
        Returns:
            BlobServiceClient instance
            
        Raises:
            ExportError: If Azure credentials not configured or library not available
        """
        try:
            from azure.storage.blob import BlobServiceClient
        except ImportError:
            raise ExportError(
                'Azure storage not available. Install: pip install azure-storage-blob'
            )
        
        # Check for required settings
        if not hasattr(settings, 'AZURE_ACCOUNT_NAME'):
            raise ExportError('AZURE_ACCOUNT_NAME not configured in settings')
        if not hasattr(settings, 'AZURE_ACCOUNT_KEY'):
            raise ExportError('AZURE_ACCOUNT_KEY not configured in settings')
        
        # Create connection string
        connection_string = (
            f"DefaultEndpointsProtocol=https;"
            f"AccountName={settings.AZURE_ACCOUNT_NAME};"
            f"AccountKey={settings.AZURE_ACCOUNT_KEY};"
            f"EndpointSuffix=core.windows.net"
        )
        
        return BlobServiceClient.from_connection_string(connection_string)
    
    def upload(self, zip_path):
        """
        Upload ZIP to Azure.
        
        Args:
            zip_path: Path to ZIP file to upload
            
        Returns:
            str: URL of uploaded blob
            
        Raises:
            ExportError: If upload fails
        """
        zip_path = Path(zip_path)
        if not zip_path.exists():
            raise ExportError(f'ZIP file not found: {zip_path}')
        
        try:
            container_client = self.blob_service.get_container_client(self.container_name)
            
            # Create container if it doesn't exist
            try:
                container_client.create_container()
            except Exception:
                # Container probably already exists
                pass
            
            # Upload with original filename
            blob_name = zip_path.name
            blob_client = container_client.get_blob_client(blob_name)
            
            with open(zip_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            
            # Also upload as "latest.zip" for easy access
            latest_blob = container_client.get_blob_client('latest.zip')
            with open(zip_path, 'rb') as data:
                latest_blob.upload_blob(data, overwrite=True)
            
            return blob_client.url
        
        except Exception as e:
            raise ExportError(f'Failed to upload to Azure: {e}')
    
    def list_backups(self):
        """
        List all backup files in the container.
        
        Returns:
            list: List of blob names
        """
        try:
            container_client = self.blob_service.get_container_client(self.container_name)
            blobs = container_client.list_blobs()
            return [blob.name for blob in blobs if blob.name.startswith('offline-backup-')]
        except Exception as e:
            raise ExportError(f'Failed to list backups: {e}')
    
    def delete_old_backups(self, keep_count=10):
        """
        Delete old backups, keeping only the most recent ones.
        
        Args:
            keep_count: Number of recent backups to keep
        """
        try:
            container_client = self.blob_service.get_container_client(self.container_name)
            
            # Get all backup blobs sorted by last modified
            blobs = []
            for blob in container_client.list_blobs():
                if blob.name.startswith('offline-backup-') and blob.name != 'latest.zip':
                    blobs.append(blob)
            
            # Sort by last modified (newest first)
            blobs.sort(key=lambda b: b.last_modified, reverse=True)
            
            # Delete old ones
            for blob in blobs[keep_count:]:
                blob_client = container_client.get_blob_client(blob.name)
                blob_client.delete_blob()
        
        except Exception as e:
            raise ExportError(f'Failed to delete old backups: {e}')
    
    def generate_sas_url(self, blob_name, expiry_hours=1):
        """
        Generate a time-limited SAS URL for download.
        
        Args:
            blob_name: Name of blob to generate URL for
            expiry_hours: Number of hours until URL expires
            
        Returns:
            str: SAS URL
        """
        try:
            from azure.storage.blob import generate_blob_sas, BlobSasPermissions
            from datetime import datetime, timedelta
        except ImportError:
            raise ExportError('Azure storage not available')
        
        sas_token = generate_blob_sas(
            account_name=settings.AZURE_ACCOUNT_NAME,
            account_key=settings.AZURE_ACCOUNT_KEY,
            container_name=self.container_name,
            blob_name=blob_name,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=expiry_hours)
        )
        
        return (
            f"https://{settings.AZURE_ACCOUNT_NAME}.blob.core.windows.net/"
            f"{self.container_name}/{blob_name}?{sas_token}"
        )
