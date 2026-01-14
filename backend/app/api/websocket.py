"""
WebSocket endpoint for real-time conversation with low latency
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from app.services.langchain_websocket import langchain_websocket_service
from app.services.session_manager import session_manager
from app.models.schemas import ScenarioConfig
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected for session {session_id}")
    
    def disconnect(self, session_id: str):
        """Remove WebSocket connection"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """Send message to specific session"""
        if session_id in self.active_connections:
            websocket = self.active_connections[session_id]
            await websocket.send_json(message)


manager = ConnectionManager()


def is_websocket_connected(websocket: WebSocket) -> bool:
    """
    Check if WebSocket connection is still active
    
    Args:
        websocket: WebSocket instance to check
        
    Returns:
        True if connected, False otherwise
    """
    return websocket.client_state != WebSocketState.DISCONNECTED


@router.websocket("/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time conversation streaming
    
    Protocol:
    - Client sends: {"type": "user_message", "content": "user input text", "turn_number": 1}
    - Server sends: {"type": "chunk", "content": "partial response"}
    - Server sends: {"type": "complete", "content": "full response"}
    - Server sends: {"type": "error", "message": "error description"}
    """
    await manager.connect(session_id, websocket)
    
    try:
        # Get session
        session = await session_manager.get_session(session_id)
        if not session:
            await websocket.send_json({
                "type": "error",
                "message": f"Session {session_id} not found"
            })
            await websocket.close()
            return
        
        # Main message loop
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_json()
                
                if data.get("type") == "user_message":
                    user_input = data.get("content", "")
                    turn_number = data.get("turn_number", 0)
                    
                    if not user_input:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Empty user message"
                        })
                        continue
                    
                    # Get conversation history
                    history = [
                        {"user": turn.user_input, "assistant": turn.ai_response}
                        for turn in session.turns
                    ]
                    
                    # Stream response using LangChain
                    full_response = ""
                    
                    try:
                        # Send start signal
                        await websocket.send_json({
                            "type": "start",
                            "turn_number": turn_number
                        })
                        
                        # Stream chunks
                        async for chunk in langchain_websocket_service.stream_response(
                            user_input, session.scenario, history
                        ):
                            full_response += chunk
                            await websocket.send_json({
                                "type": "chunk",
                                "content": chunk
                            })
                        
                        # Send completion signal with full response
                        await websocket.send_json({
                            "type": "complete",
                            "content": full_response,
                            "turn_number": turn_number
                        })
                        
                    except Exception as e:
                        logger.error(f"Error streaming response: {str(e)}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error generating response: {str(e)}"
                        })
                
                elif data.get("type") == "ping":
                    # Heartbeat
                    await websocket.send_json({"type": "pong"})
                
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown message type: {data.get('type')}"
                    })
                    
            except WebSocketDisconnect:
                logger.info(f"Client disconnected from session {session_id}")
                break
            except json.JSONDecodeError:
                # Only send error if connection is still active
                if is_websocket_connected(websocket):
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": "Invalid JSON format"
                        })
                    except Exception:
                        pass  # Connection already closed
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                # Only send error if connection is still active
                if is_websocket_connected(websocket):
                    try:
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Internal error: {str(e)}"
                        })
                    except Exception:
                        pass  # Connection already closed
                
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        manager.disconnect(session_id)
