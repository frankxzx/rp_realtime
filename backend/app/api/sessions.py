from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.models.schemas import (
    StartSessionRequest, StartSessionResponse, TurnFeedback,
    SnapshotSubmission, AssessmentReport
)
from app.services.session_manager import session_manager
from app.services.audio_processor import audio_processor
from app.core.config import settings
import base64
from typing import Optional

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/start", response_model=StartSessionResponse)
async def start_session(request: StartSessionRequest):
    """Start a new conversation session"""
    session = await session_manager.create_session(request.scenario)
    
    return StartSessionResponse(
        session_id=session.session_id,
        scenario=session.scenario,
        max_recording_duration=settings.max_recording_duration,
        snapshot_interval=settings.snapshot_interval
    )


@router.post("/{session_id}/turns", response_model=TurnFeedback)
async def submit_turn(
    session_id: str,
    turn_number: int = Form(...),
    user_input: str = Form(...),
    audio_file: UploadFile = File(...)
):
    """
    Submit a conversation turn with audio
    
    Args:
        session_id: Session ID
        turn_number: Current turn number
        user_input: Transcribed user input
        audio_file: MP3 audio file
    """
    try:
        # Read audio file
        audio_data = await audio_file.read()
        
        # Process the turn
        feedback = await session_manager.process_turn(
            session_id, turn_number, user_input, audio_data
        )
        
        return feedback
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing turn: {str(e)}")


@router.post("/{session_id}/snapshots")
async def submit_snapshot(session_id: str, snapshot: SnapshotSubmission):
    """Submit a camera snapshot"""
    try:
        snapshot_url = await session_manager.add_snapshot(
            session_id, snapshot.image_data
        )
        return {"snapshot_url": snapshot_url}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading snapshot: {str(e)}")


@router.post("/{session_id}/complete", response_model=AssessmentReport)
async def complete_session(session_id: str):
    """
    Complete the session and generate final assessment report
    """
    try:
        report = await session_manager.generate_assessment_report(session_id)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session details"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
