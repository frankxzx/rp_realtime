from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ScenarioConfig(BaseModel):
    """Configuration for conversation scenario"""
    context: str = Field(..., description="What scenario/context for the conversation")
    target_audience: str = Field(..., description="Background of the person being practiced with")
    purpose: str = Field(..., description="Purpose of the conversation practice")
    target_language: str = Field(default="English", description="Language to practice")
    custom_prompt: Optional[str] = Field(None, description="Additional custom instructions")


class AudioChunk(BaseModel):
    """Audio chunk data"""
    chunk_data: bytes
    timestamp: datetime
    chunk_index: int


class TurnFeedback(BaseModel):
    """Feedback for a single conversation turn"""
    turn_number: int
    user_input: str
    ai_response: str
    ideal_answer: Optional[str] = None
    suggestions: List[str] = []
    scores: Dict[str, float] = {}
    insights: List[str] = []
    direction: str = ""
    audio_url: Optional[str] = None


class VisualAnalysis(BaseModel):
    """Analysis of visual data (facial expressions, body language)"""
    facial_expression: str
    body_language: str
    confidence_level: str
    engagement_indicators: List[str] = []


class AudioAnalysis(BaseModel):
    """Analysis of audio tone and delivery"""
    tone: str
    pace: str
    clarity: str
    emotional_indicators: List[str] = []


class AssessmentReport(BaseModel):
    """Final assessment report"""
    session_id: str
    scenario: ScenarioConfig
    turns: List[TurnFeedback]
    visual_analysis: VisualAnalysis
    audio_analysis: AudioAnalysis
    overall_scores: Dict[str, float] = {}
    summary: str
    recommendations: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationSession(BaseModel):
    """Conversation session data"""
    session_id: str
    scenario: ScenarioConfig
    turns: List[TurnFeedback] = []
    snapshots: List[str] = []  # URLs to snapshot images
    status: str = "active"  # active, completed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecordingRequest(BaseModel):
    """Request to start recording"""
    session_id: str
    turn_number: int


class AudioSubmission(BaseModel):
    """Audio submission with metadata"""
    session_id: str
    turn_number: int
    audio_data: str  # base64 encoded audio
    duration: float


class SnapshotSubmission(BaseModel):
    """Camera snapshot submission"""
    session_id: str
    image_data: str  # base64 encoded image
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StartSessionRequest(BaseModel):
    """Request to start a new conversation session"""
    scenario: ScenarioConfig


class StartSessionResponse(BaseModel):
    """Response when starting a new session"""
    session_id: str
    scenario: ScenarioConfig
    max_recording_duration: int
    snapshot_interval: int
