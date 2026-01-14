from azure.storage.blob import BlobServiceClient, ContentSettings
from app.core.config import settings
import base64
from datetime import datetime
import uuid
from typing import Optional


class BlobStorageService:
    """Service for Azure Blob Storage operations"""
    
    def __init__(self):
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.azure_storage_connection_string
        )
        self.audio_container = settings.azure_storage_container_audio
        self.images_container = settings.azure_storage_container_images
        
    async def upload_audio(
        self, 
        audio_data: bytes, 
        session_id: str, 
        turn_number: int
    ) -> str:
        """Upload audio file to blob storage"""
        blob_name = f"{session_id}/turn_{turn_number}_{uuid.uuid4()}.mp3"
        blob_client = self.blob_service_client.get_blob_client(
            container=self.audio_container,
            blob=blob_name
        )
        
        content_settings = ContentSettings(content_type='audio/mpeg')
        blob_client.upload_blob(
            audio_data, 
            overwrite=True,
            content_settings=content_settings
        )
        
        return blob_client.url
    
    async def upload_image(
        self, 
        image_data: str, 
        session_id: str
    ) -> str:
        """Upload snapshot image to blob storage"""
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        
        blob_name = f"{session_id}/snapshot_{uuid.uuid4()}.jpg"
        blob_client = self.blob_service_client.get_blob_client(
            container=self.images_container,
            blob=blob_name
        )
        
        content_settings = ContentSettings(content_type='image/jpeg')
        blob_client.upload_blob(
            image_bytes, 
            overwrite=True,
            content_settings=content_settings
        )
        
        return blob_client.url
    
    async def get_session_snapshots(self, session_id: str) -> list:
        """Get all snapshot URLs for a session"""
        container_client = self.blob_service_client.get_container_client(
            self.images_container
        )
        
        blob_list = container_client.list_blobs(name_starts_with=f"{session_id}/")
        return [blob.name for blob in blob_list]


blob_storage_service = BlobStorageService()
