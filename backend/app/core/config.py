from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Azure OpenAI Configuration
    azure_openai_api_key: str
    azure_openai_endpoint: str
    azure_openai_deployment_name: str = "gpt-mini-realtime"
    azure_openai_api_version: str = "2024-10-01-preview"
    
    # Azure Blob Storage Configuration
    azure_storage_connection_string: str
    azure_storage_container_audio: str = "audio-recordings"
    azure_storage_container_images: str = "camera-snapshots"
    
    # Application Configuration
    max_recording_duration: int = 60
    snapshot_interval: int = 5
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Scoring Dimensions
    scoring_dimensions: str = "fluency,accuracy,relevance,confidence,engagement"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def scoring_dimensions_list(self) -> List[str]:
        return [dim.strip() for dim in self.scoring_dimensions.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
