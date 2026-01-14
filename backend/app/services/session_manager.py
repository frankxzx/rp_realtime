from app.models.schemas import (
    ConversationSession, TurnFeedback, AssessmentReport,
    VisualAnalysis, AudioAnalysis, ScenarioConfig
)
from app.services.realtime_api import realtime_api_service
from app.services.scoring import scoring_service
from app.services.blob_storage import blob_storage_service
from app.services.audio_processor import audio_processor
from app.core.qa_data import get_ideal_answer
from typing import Dict, List
import uuid
from datetime import datetime


class SessionManager:
    """Manage conversation sessions"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
    
    async def create_session(self, scenario: ScenarioConfig) -> ConversationSession:
        """Create a new conversation session"""
        session_id = str(uuid.uuid4())
        session = ConversationSession(
            session_id=session_id,
            scenario=scenario,
            turns=[],
            snapshots=[],
            status="active"
        )
        self.sessions[session_id] = session
        return session
    
    async def get_session(self, session_id: str) -> ConversationSession:
        """Get an existing session"""
        return self.sessions.get(session_id)
    
    async def process_turn(
        self,
        session_id: str,
        turn_number: int,
        user_input: str,
        audio_data: bytes
    ) -> TurnFeedback:
        """
        Process a conversation turn and generate feedback
        
        Args:
            session_id: Session ID
            turn_number: Current turn number
            user_input: User's transcribed input
            audio_data: MP3 audio data
            
        Returns:
            TurnFeedback with all analysis
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Upload audio to blob storage
        audio_url = await blob_storage_service.upload_audio(
            audio_data, session_id, turn_number
        )
        
        # Get conversation history
        history = [
            {"user": turn.user_input, "assistant": turn.ai_response}
            for turn in session.turns
        ]
        
        # Generate AI response
        ai_response = await realtime_api_service.generate_response(
            user_input, session.scenario, history
        )
        
        # Get ideal answer from Q&A data
        ideal_answer = get_ideal_answer(session.scenario.context, user_input)
        
        # Generate suggestions
        suggestions = await realtime_api_service.generate_suggestions(
            user_input, ideal_answer, session.scenario
        )
        
        # Generate insights
        insights = await realtime_api_service.generate_insights(
            user_input, session.scenario
        )
        
        # Generate direction
        direction = await realtime_api_service.generate_direction(
            user_input, session.scenario
        )
        
        # Score the response
        scores = await scoring_service.score_response(
            user_input, ideal_answer, session.scenario.context
        )
        
        # Create turn feedback
        feedback = TurnFeedback(
            turn_number=turn_number,
            user_input=user_input,
            ai_response=ai_response,
            ideal_answer=ideal_answer,
            suggestions=suggestions,
            scores=scores,
            insights=insights,
            direction=direction,
            audio_url=audio_url
        )
        
        # Add to session
        session.turns.append(feedback)
        session.updated_at = datetime.utcnow()
        
        return feedback
    
    async def add_snapshot(self, session_id: str, image_data: str) -> str:
        """Add a camera snapshot to the session"""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Upload snapshot to blob storage
        snapshot_url = await blob_storage_service.upload_image(
            image_data, session_id
        )
        
        session.snapshots.append(snapshot_url)
        session.updated_at = datetime.utcnow()
        
        return snapshot_url
    
    async def generate_assessment_report(
        self, 
        session_id: str
    ) -> AssessmentReport:
        """
        Generate final assessment report for the session
        
        Args:
            session_id: Session ID
            
        Returns:
            Complete assessment report
        """
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        # Analyze visual data (facial expressions, body language)
        visual_data = await realtime_api_service.analyze_visual(session.snapshots)
        visual_analysis = VisualAnalysis(**visual_data)
        
        # Analyze audio across all turns
        audio_analyses = []
        for turn in session.turns:
            # Note: In production, you'd fetch audio from blob and analyze
            # For now, using placeholder
            audio_analyses.append({
                "tone": "confident",
                "pace": "moderate",
                "clarity": "clear"
            })
        
        # Aggregate audio analysis
        audio_analysis = AudioAnalysis(
            tone="varied and engaged",
            pace="moderate",
            clarity="clear",
            emotional_indicators=["engaged", "confident"]
        )
        
        # Calculate overall scores
        turn_scores = [turn.scores for turn in session.turns]
        overall_scores = await scoring_service.calculate_overall_scores(turn_scores)
        
        # Generate summary and recommendations
        summary = await self._generate_summary(session, overall_scores)
        recommendations = await self._generate_recommendations(session, overall_scores)
        
        # Create assessment report
        report = AssessmentReport(
            session_id=session_id,
            scenario=session.scenario,
            turns=session.turns,
            visual_analysis=visual_analysis,
            audio_analysis=audio_analysis,
            overall_scores=overall_scores,
            summary=summary,
            recommendations=recommendations
        )
        
        # Mark session as completed
        session.status = "completed"
        session.updated_at = datetime.utcnow()
        
        return report
    
    async def _generate_summary(
        self, 
        session: ConversationSession, 
        overall_scores: Dict[str, float]
    ) -> str:
        """Generate assessment summary"""
        avg_score = sum(overall_scores.values()) / len(overall_scores) if overall_scores else 0
        
        summary = f"Completed {len(session.turns)} conversation turns practicing {session.scenario.purpose}. "
        summary += f"Overall performance score: {avg_score:.1f}/10. "
        
        # Highlight strengths
        best_dimension = max(overall_scores.items(), key=lambda x: x[1]) if overall_scores else ("N/A", 0)
        summary += f"Strongest area: {best_dimension[0]} ({best_dimension[1]:.1f}/10). "
        
        return summary
    
    async def _generate_recommendations(
        self, 
        session: ConversationSession, 
        overall_scores: Dict[str, float]
    ) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []
        
        # Find weakest dimension
        if overall_scores:
            weakest = min(overall_scores.items(), key=lambda x: x[1])
            recommendations.append(
                f"Focus on improving {weakest[0]} (current score: {weakest[1]:.1f}/10)"
            )
        
        # Add general recommendations
        recommendations.extend([
            "Continue practicing regularly to build confidence",
            "Record yourself and review to identify areas for improvement",
            "Focus on clear articulation and maintaining steady pace"
        ])
        
        return recommendations[:5]


session_manager = SessionManager()
