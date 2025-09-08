"""
WhatsApp Routes

Contains WhatsApp webhook endpoints for receiving and processing messages.
This module will handle WhatsApp Business API integration to forward messages
to the AI service and send responses back to WhatsApp users.

TODO: Implement WhatsApp Business API integration
- Webhook verification endpoint
- Message receiving endpoint
- Message sending functionality
- Integration with AI service
"""

from fastapi import APIRouter, HTTPException, Request, status
from app.models.request import ChatRequest
from app.services.ai_service import process_chat_message
from app.services.whatsapp_service import (
    verify_webhook,
    process_whatsapp_message,
    send_whatsapp_message
)
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/whatsapp/webhook")
async def whatsapp_webhook_verification(request: Request):
    """
    WhatsApp webhook verification endpoint.
    
    This endpoint is called by WhatsApp to verify the webhook URL.
    It should return the challenge parameter sent by WhatsApp.
    
    Args:
        request (Request): The incoming request from WhatsApp
        
    Returns:
        str: The challenge parameter for verification
        
    TODO: Implement actual webhook verification logic
    """
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"WhatsApp webhook verification: mode={mode}, token={token}")
        
        # TODO: Verify the webhook token matches your configured token
        if verify_webhook(mode, token):
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Webhook verification failed"
            )
            
    except Exception as e:
        logger.error(f"Error in WhatsApp webhook verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook verification error"
        )

@router.post("/whatsapp/webhook")
async def whatsapp_webhook_handler(request: Request):
    """
    WhatsApp webhook message handler.
    
        dict: Success response
        
    TODO: Implement message processing and response logic
    """
    try:
        # Get the webhook payload
        payload = await request.json()
        logger.info(f"Received WhatsApp webhook: {payload}")
        
        # Process the WhatsApp message
        message_data = await process_whatsapp_message(payload)
        
        if message_data:
            # Extract message content and sender info
            user_message = message_data.get("message")
            sender_phone = message_data.get("from")
            
            if user_message and sender_phone:
                # Process through AI service
                ai_response = await process_chat_message(user_message)
                
                # Send response back to WhatsApp
                await send_whatsapp_message(sender_phone, ai_response)
                
                logger.info(f"Processed WhatsApp message from {sender_phone}")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {str(e)}")
        # Don't raise HTTP exception here - WhatsApp expects 200 OK
        # Log the error but return success to avoid webhook retries
        return {"status": "error", "message": str(e)}

@router.get("/whatsapp/status")
async def whatsapp_status():
    """
    
    """
    return {
        "service": "whatsapp",
        "status": "placeholder",
        "message": "WhatsApp integration endpoints ready for implementation",
        "endpoints": {
            "webhook_verification": "/api/v1/whatsapp/webhook (GET)",
            "webhook_handler": "/api/v1/whatsapp/webhook (POST)",
            "status": "/api/v1/whatsapp/status (GET)"
        },
        "todo": [
            "Configure WhatsApp Business API credentials",
            "Implement webhook verification logic",
            "Implement message parsing and response logic",
            "Add error handling and retry mechanisms",
            "Add message formatting for WhatsApp"
        ]
    }