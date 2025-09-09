"""
AI Service

This module contains the AI integration logic. It integrates with both
direct Gemini API calls and LangChain pipeline for enhanced conversation
handling with memory and system prompts.
"""

import asyncio
import logging
from typing import Optional
from app.services.gemini_service import generate_gemini_response, get_gemini_service_status
from app.services.ai_chain import process_with_langchain, get_langchain_status

# Configure logging
logger = logging.getLogger(__name__)

async def process_chat_message(message: str, use_langchain: bool = True, session_id: Optional[str] = None) -> str:
    """
    Process a chat message and return an AI-generated response.
    
    This function can use either:
    1. LangChain pipeline (default) - with conversation memory and system prompts
    2. Direct Gemini API calls - for simple responses without memory
    
    The LangChain approach is recommended for conversational experiences.
    
    Args:
        message (str): The user's input message
        use_langchain (bool): Whether to use LangChain pipeline (default: True)
        session_id (Optional[str]): Session ID for conversation tracking
        
    Returns:
        str: The AI-generated response
    """
    try:
        # Log the processing request
        method = "LangChain" if use_langchain else "Direct Gemini"
        logger.info(f"Processing chat message via {method}: {message[:50]}...")
        
        if use_langchain:
            # Use LangChain pipeline with conversation memory
            ai_response = await process_with_langchain(message, session_id)
        else:
            # Use direct Gemini API call (legacy method)
            ai_response = await generate_gemini_response(message)
        
        logger.info(f"Generated AI response via {method}: {ai_response[:50]}...")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in AI service: {str(e)}")
        
        # Try fallback method if primary fails
        if use_langchain:
            logger.info("LangChain failed, trying direct Gemini API as fallback")
            try:
                return await generate_gemini_response(message)
            except Exception as fallback_error:
                logger.error(f"Fallback also failed: {str(fallback_error)}")
        
        # Return user-friendly fallback response
        return "Desculpe, estou enfrentando dificuldades técnicas no momento. Por favor, tente novamente em instantes."

async def get_ai_service_status() -> dict:
    """
    Get the current status of the AI service including both Gemini and LangChain.
    
    Returns:
        dict: Comprehensive status information about all AI services
    """
    try:
        # Get status from both services
        gemini_status = await get_gemini_service_status()
        langchain_status = get_langchain_status()
        
        # Determine overall status
        overall_status = "active"
        if gemini_status["status"] != "active" and langchain_status["status"] != "active":
            overall_status = "degraded"
        elif gemini_status["status"] == "configuration_required" and langchain_status["status"] == "configuration_required":
            overall_status = "configuration_required"
        
        return {
            "service": "ai_service",
            "status": overall_status,
            "primary_method": "langchain_pipeline",
            "fallback_method": "direct_gemini_api",
            "ready_for_integration": True,
            "supported_features": [
                "intelligent_chat",
                "conversation_memory",
                "system_prompts",
                "message_processing",
                "error_handling",
                "fallback_responses",
                "session_management"
            ],
            "services": {
                "langchain": langchain_status,
                "gemini_direct": gemini_status
            },
            "usage_recommendations": [
                "Use LangChain for conversational experiences (default)",
                "Use direct Gemini for simple, stateless responses",
                "LangChain provides conversation memory and system prompts",
                "Automatic fallback to direct Gemini if LangChain fails"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting AI service status: {str(e)}")
        return {
            "service": "ai_service",
            "status": "error",
            "error": str(e)
        }

# Configuration for future AI integrations
AI_CONFIG = {
    "max_tokens": 300,  # Updated to match LangChain config
    "temperature": 0.7,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "fallback_message": "Desculpe, estou enfrentando dificuldades técnicas. Tente novamente em instantes.",
    "use_langchain_by_default": True,
    "enable_conversation_memory": True
}