"""
WhatsApp Service

This module integrates with Evolution API for WhatsApp messaging.
It handles message processing, sending, and webhook management through Evolution API.
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from app.services.evolution_service import evolution_service
from app.services.ai_service import process_chat_message

# Configure logging
logger = logging.getLogger(__name__)

async def verify_webhook(mode: str, token: str) -> bool:
    """
    Verify Evolution API webhook token.
    
    Args:
        mode (str): The hub mode from Evolution API
        token (str): The verify token from Evolution API
        
    Returns:
        bool: True if verification is successful
    """
    try:
        logger.info(f"Verifying Evolution API webhook: mode={mode}, token={token}")
        
        # Evolution API uses different verification method
        # For now, we'll accept the webhook if it contains the expected token
        expected_token = evolution_service.api_key
        if token == expected_token:
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error verifying webhook: {str(e)}")
        return False

async def process_whatsapp_message(payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """
    Process incoming Evolution API webhook payload and extract message data.
    
    Args:
        payload (Dict[str, Any]): The webhook payload from Evolution API
        
    Returns:
        Optional[Dict[str, str]]: Extracted message data or None
    """
    try:
        logger.info("Processing Evolution API webhook payload")
        return await evolution_service.process_webhook_message(payload)
        
    except Exception as e:
        logger.error(f"Error processing Evolution API message: {str(e)}")
        return None

async def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """
    Send a message to a WhatsApp user via Evolution API.
    
    Args:
        phone_number (str): The recipient's phone number
        message (str): The message to send
        
    Returns:
        bool: True if message was sent successfully
    """
    try:
        logger.info(f"Sending WhatsApp message via Evolution API to {phone_number}")
        
        result = await evolution_service.send_message(phone_number, message)
        
        if result:
            logger.info(f"Message sent successfully to {phone_number}")
            return True
        else:
            logger.error(f"Failed to send message to {phone_number}")
            return False
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message via Evolution API: {str(e)}")
        return False

async def process_incoming_message(message_data: Dict[str, str]) -> bool:
    """
    Process incoming WhatsApp message and send AI response.
    
    Args:
        message_data (Dict[str, str]): Message data from webhook
        
    Returns:
        bool: True if processed successfully
    """
    try:
        user_message = message_data.get("message", "")
        sender_phone = message_data.get("from", "")
        
        if not user_message or not sender_phone:
            logger.warning("Invalid message data received")
            return False
        
        logger.info(f"Processing incoming WhatsApp message from {sender_phone}: {user_message}")
        
        # Process through AI service
        ai_response = await process_chat_message(user_message, use_langchain=True)
        
        # Send response back to WhatsApp
        success = await send_whatsapp_message(sender_phone, ai_response)
        
        if success:
            logger.info(f"Successfully processed and responded to message from {sender_phone}")
        else:
            logger.error(f"Failed to send response to {sender_phone}")
        
        return success
        
    except Exception as e:
        logger.error(f"Error processing incoming WhatsApp message: {str(e)}")
        return False

async def get_whatsapp_service_status() -> Dict[str, Any]:
    """
    Get the current status of the WhatsApp service via Evolution API.
    
    Returns:
        Dict[str, Any]: Status information about the WhatsApp service
    """
    try:
        evolution_status = await evolution_service.get_service_status()
        
        return {
            "service": "whatsapp_service",
            "status": evolution_status.get("status", "error"),
            "implementation": "evolution_api_integration",
            "evolution_api": evolution_status,
            "supported_features": [
                "webhook_verification",
                "message_receiving", 
                "message_sending",
                "qr_code_authentication",
                "ai_response_integration",
                "error_handling"
            ],
            "integration_status": "active" if evolution_status.get("status") == "active" else "needs_setup"
        }
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp service status: {str(e)}")
        return {
            "service": "whatsapp_service",
            "status": "error",
            "error": str(e),
            "implementation": "evolution_api_integration"
        }

async def initialize_whatsapp_service() -> Dict[str, Any]:
    """
    Initialize the WhatsApp service via Evolution API.
    
    Returns:
        Dict[str, Any]: Initialization result
    """
    try:
        logger.info("Initializing WhatsApp service via Evolution API")
        return await evolution_service.initialize_instance()
        
    except Exception as e:
        logger.error(f"Error initializing WhatsApp service: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to initialize WhatsApp service"
        }

# Helper function to format messages for WhatsApp
def format_message_for_whatsapp(message: str) -> str:
    """
    Format AI response message for WhatsApp display.
    
    Args:
        message (str): The original AI response
        
    Returns:
        str: Formatted message for WhatsApp
    """
    try:
        # WhatsApp message length limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "..."
        
        # Add some basic formatting for better mobile display
        # Replace markdown-style formatting with WhatsApp formatting
        message = message.replace("**", "*")  # Bold
        message = message.replace("__", "_")  # Italic
        
        # Ensure proper line breaks for mobile
        message = message.replace("\n\n", "\n")
        
        return message.strip()
        
    except Exception as e:
        logger.error(f"Error formatting message for WhatsApp: {str(e)}")
        return message  # Return original if formatting fails