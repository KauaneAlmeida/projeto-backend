from fastapi import APIRouter, HTTPException, status
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services.ai_service import process_chat_message
from app.services.gemini_service import get_gemini_service_status, test_gemini_connection
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
 
    try:
        # Log the incoming request
        logger.info(f"Received chat message: {request.message}")
        
        # Validate message content
        if not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )
        
        # Process the message through AI service
        ai_reply = await process_chat_message(request.message)
        
        # Create and return response
        response = ChatResponse(reply=ai_reply)
        logger.info(f"Sending reply: {response.reply}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log and handle unexpected errors
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )

@router.get("/chat/status")
async def chat_status():
    """
    Get the status of the chat service and underlying AI service.
    
    Returns:
        dict: Comprehensive status information including Gemini API status
    """
    try:
        # Get AI service status (includes Gemini details)
        from app.services.ai_service import get_ai_service_status
        ai_status = await get_ai_service_status()
        
        # Test Gemini connection
        gemini_connected = await test_gemini_connection()
        
        return {
            "service": "chat",
            "status": "active",
            "message": "Chat service is running and ready to process messages",
            "status": "degraded",
            "message": "Chat service is running but AI integration may have issues",
            "error": str(e)
        }
        
    except Exception as e:
        logger.error(f"Error getting chat status: {str(e)}")
    return {
        "service": "chat",
        "status": "active",
        "message": "Chat service is running and ready to process messages"
    }