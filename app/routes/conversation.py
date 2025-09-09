"""
Conversation Flow Routes

This module handles the guided conversation flow for law firm client intake.
It manages step-by-step questions, collects lead information, and transitions
to AI-powered chat when the flow is completed.

Lawyers can update the conversation flow directly in Firebase Console
without modifying this code.
"""

from fastapi import APIRouter, HTTPException, status
from app.models.request import ConversationRequest
from app.models.response import ConversationResponse
from app.services.conversation_service import conversation_manager
from app.services.firebase_service import get_firebase_service_status
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/conversation/start", response_model=ConversationResponse)
async def start_conversation():
    """
    Start a new guided conversation flow.
    
    This endpoint initializes a new conversation session and returns
    the first question in the law firm intake flow.
    
    Returns:
        ConversationResponse: First question and session information
    """
    try:
        logger.info("Starting new conversation flow")
        
        result = await conversation_manager.start_conversation()
        
        return ConversationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error starting conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start conversation"
        )

@router.post("/conversation/respond", response_model=ConversationResponse)
async def respond_to_conversation(request: ConversationRequest):
    """
    Process user response in the conversation flow.
    
    This endpoint handles user responses to guided questions and either:
    1. Returns the next question in the flow
    2. Completes the flow and saves lead data
    3. Processes the message through AI if flow is completed
    
    Args:
        request (ConversationRequest): User response and session ID
        
    Returns:
        ConversationResponse: Next question or AI response
    """
    try:
        logger.info(f"Processing conversation response for session: {request.session_id}")
        
        if not request.session_id:
            # No session ID provided, start new conversation
            result = await conversation_manager.start_conversation()
        else:
            # Process response in existing session
            result = await conversation_manager.process_response(
                request.session_id, 
                request.message
            )
        
        return ConversationResponse(**result)
        
    except Exception as e:
        logger.error(f"Error processing conversation response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process conversation response"
        )

@router.get("/conversation/status/{session_id}")
async def get_conversation_status(session_id: str):
    """
    Get the current status of a conversation session.
    
    Args:
        session_id (str): The session identifier
        
    Returns:
        dict: Current conversation state and progress
    """
    try:
        logger.info(f"Getting conversation status for session: {session_id}")
        
        status_info = await conversation_manager.get_conversation_status(session_id)
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error getting conversation status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get conversation status"
        )

@router.get("/conversation/flow")
async def get_conversation_flow():
    """
    Get the current conversation flow configuration.
    
    This endpoint returns the flow structure that lawyers can modify
    in Firebase Console. Useful for debugging and frontend integration.
    
    Returns:
        dict: Current conversation flow configuration
    """
    try:
        logger.info("Retrieving conversation flow configuration")
        
        flow = await conversation_manager.get_flow()
        
        return {
            "flow": flow,
            "total_steps": len(flow.get("steps", [])),
            "editable_in": "Firebase Console > conversation_flows > law_firm_intake",
            "note": "Lawyers can update questions without touching the code"
        }
        
    except Exception as e:
        logger.error(f"Error retrieving conversation flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation flow"
        )

@router.get("/conversation/service-status")
async def conversation_service_status():
    """
    Get the status of the conversation service and its dependencies.
    
    Returns:
        dict: Service status including Firebase connectivity
    """
    try:
        # Get Firebase status
        firebase_status = await get_firebase_service_status()
        
        # Test conversation flow retrieval
        try:
            flow = await conversation_manager.get_flow()
            flow_accessible = True
            total_steps = len(flow.get("steps", []))
        except Exception as e:
            flow_accessible = False
            total_steps = 0
            logger.error(f"Flow access test failed: {str(e)}")
        
        return {
            "service": "conversation_service",
            "status": "active" if firebase_status["status"] == "active" and flow_accessible else "degraded",
            "firebase_status": firebase_status,
            "conversation_flow": {
                "accessible": flow_accessible,
                "total_steps": total_steps,
                "editable_location": "Firebase Console > conversation_flows > law_firm_intake"
            },
            "features": [
                "guided_intake_flow",
                "lead_data_collection", 
                "ai_mode_transition",
                "session_management"
            ],
            "endpoints": {
                "start": "/api/v1/conversation/start",
                "respond": "/api/v1/conversation/respond", 
                "status": "/api/v1/conversation/status/{session_id}",
                "flow": "/api/v1/conversation/flow"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation service status: {str(e)}")
        return {
            "service": "conversation_service",
            "status": "error",
            "error": str(e)
        }