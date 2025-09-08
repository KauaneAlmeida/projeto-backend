"""
AI Service

This module contains the AI integration logic. It now integrates with
Google's Gemini API for generating intelligent responses to user messages.
"""

import asyncio
import logging
from app.services.gemini_service import generate_gemini_response, get_gemini_service_status

# Configure logging
logger = logging.getLogger(__name__)

async def process_chat_message(message: str) -> str:
    """
    Process a chat message and return an AI-generated response.
    
    This function now uses Google's Gemini API to generate intelligent responses
    to user messages. It includes fallback handling for when the API is unavailable.
    
    Args:
        message (str): The user's input message
        
    Returns:
        str: The AI-generated response
    """
    try:
        # Log the processing request
        logger.info(f"Processing chat message: {message}")
        
        # Use Gemini API to generate response
        ai_response = await generate_gemini_response(message)
        
        logger.info(f"Generated AI response: {ai_response}")
        return ai_response
        
    except Exception as e:
        logger.error(f"Error in AI service: {str(e)}")
        # Return a fallback response for better user experience
        return "I'm sorry, I'm experiencing technical difficulties right now. Please try again in a moment."

async def get_ai_service_status() -> dict:
    """
    Get the current status of the AI service.
    
    Returns:
        dict: Status information about the AI service
    """
    # Get Gemini service status
    gemini_status = await get_gemini_service_status()
    
    base_status = {
        "service": "ai_service",
        "status": gemini_status["status"],
        "implementation": "google_gemini_api",
        "ready_for_integration": True,
        "supported_features": [
            "intelligent_chat",
            "message_processing",
            "error_handling",
            "fallback_responses"
        ]
    }
    
    # Merge with Gemini-specific status
    base_status.update({
        "gemini_details": gemini_status
    })
    
    return base_status

# Configuration for future AI integrations
AI_CONFIG = {
    "max_tokens": 1000,
    "temperature": 0.7,
    "timeout_seconds": 30,
    "retry_attempts": 3,
    "fallback_message": "I'm experiencing technical difficulties. Please try again in a moment."
}