import base64
import io
from pydub import AudioSegment
import numpy as np
from typing import List


class AudioProcessor:
    """Service for processing audio data"""
    
    @staticmethod
    def pcm_to_mp3(pcm_chunks: List[bytes], sample_rate: int = 16000) -> bytes:
        """
        Convert PCM audio chunks to a single MP3 file
        
        Args:
            pcm_chunks: List of PCM audio chunk bytes
            sample_rate: Sample rate of the audio (default 16000 Hz)
            
        Returns:
            MP3 audio data as bytes
        """
        # Combine all PCM chunks
        combined_pcm = b''.join(pcm_chunks)
        
        # Convert PCM to AudioSegment
        # Assuming 16-bit PCM, mono channel
        audio_segment = AudioSegment(
            data=combined_pcm,
            sample_width=2,  # 16-bit = 2 bytes
            frame_rate=sample_rate,
            channels=1  # mono
        )
        
        # Export as MP3
        mp3_buffer = io.BytesIO()
        audio_segment.export(mp3_buffer, format="mp3", bitrate="128k")
        mp3_buffer.seek(0)
        
        return mp3_buffer.read()
    
    @staticmethod
    def base64_to_pcm(base64_data: str) -> bytes:
        """Convert base64 encoded audio to PCM bytes"""
        return base64.b64decode(base64_data)
    
    @staticmethod
    def analyze_audio_tone(audio_data: bytes) -> dict:
        """
        Analyze audio tone characteristics
        This is a simplified version - in production, you'd use more sophisticated audio analysis
        
        Args:
            audio_data: Audio data in bytes
            
        Returns:
            Dictionary with tone analysis
        """
        try:
            # Load audio
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Basic analysis
            duration = len(audio_segment) / 1000.0  # duration in seconds
            loudness = audio_segment.dBFS  # loudness in dBFS
            
            # Determine tone based on simple heuristics
            tone = "neutral"
            if loudness > -10:
                tone = "energetic"
            elif loudness < -25:
                tone = "soft"
            
            # Determine pace based on duration
            pace = "moderate"
            if duration < 3:
                pace = "fast"
            elif duration > 10:
                pace = "slow"
            
            # Clarity is harder to determine without speech recognition
            # This is a placeholder
            clarity = "clear" if loudness > -30 else "unclear"
            
            return {
                "tone": tone,
                "pace": pace,
                "clarity": clarity,
                "duration": duration,
                "loudness": loudness,
                "emotional_indicators": [
                    f"{tone} delivery",
                    f"{pace} speaking pace"
                ]
            }
        except Exception as e:
            return {
                "tone": "neutral",
                "pace": "moderate",
                "clarity": "clear",
                "duration": 0,
                "loudness": 0,
                "emotional_indicators": []
            }


audio_processor = AudioProcessor()
