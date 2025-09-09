from fastapi import APIRouter, HTTPException, status
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.services.ai_service import process_chat_message
from app.services.ai_service import get_ai_service_status
from app.services.ai_chain import clear_conversation_memory
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
        # Use LangChain by default for enhanced conversation experience
        ai_reply = await process_chat_message(
            message=request.message,
            use_langchain=True,
            session_id=request.session_id
        )
        
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
    Get the status of the chat service and underlying AI services (LangChain + Gemini).
    
    Returns:
        dict: Comprehensive status information including LangChain and Gemini status
    """
    try:
        # Get comprehensive AI service status
        ai_status = await get_ai_service_status()
        
        return {
            "service": "chat",
            "status": "active" if ai_status["status"] in ["active", "degraded"] else "configuration_required",
            "message": "Chat service is running with LangChain + Gemini integration",
            "ai_integration": ai_status,
            "features": [
                "langchain_conversation_memory",
                "system_prompt_support",
                "gemini_api_integration",
                "automatic_fallback",
                "session_management",
                "brazilian_portuguese_responses"
            ],
            "endpoints": {
                "chat": "/api/v1/chat",
                "status": "/api/v1/chat/status",
                "clear_memory": "/api/v1/chat/clear-memory"
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting chat status: {str(e)}")