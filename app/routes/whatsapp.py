"""
WhatsApp Routes

Contains WhatsApp webhook endpoints for receiving and processing messages via Evolution API.
This module handles Evolution API integration to forward messages to the AI service 
and send responses back to WhatsApp users.
"""

from fastapi import APIRouter, HTTPException, Request, status
from app.models.request import ChatRequest
from app.services.whatsapp_service import (
    verify_webhook,
    process_whatsapp_message,
    send_whatsapp_message,
    get_whatsapp_service_status,
    initialize_whatsapp_service,
    process_incoming_message
)
from app.services.evolution_service import evolution_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/whatsapp/webhook")
async def evolution_webhook_verification(request: Request):
    """
    Evolution API webhook verification endpoint.
    
    This endpoint is called by Evolution API to verify the webhook URL.
    It should return the challenge parameter sent by Evolution API.
    
    Args:
        request (Request): The incoming request from Evolution API
        
    Returns:
        str: The challenge parameter for verification
    """
    try:
        # Get query parameters
        mode = request.query_params.get("hub.mode")
        token = request.query_params.get("hub.verify_token")
        challenge = request.query_params.get("hub.challenge")
        
        logger.info(f"Evolution API webhook verification: mode={mode}, token={token}")
        
        # Verify the webhook token matches our configured token
        if verify_webhook(mode, token):
            logger.info("Evolution API webhook verified successfully")
            return challenge
        else:
            logger.warning("Evolution API webhook verification failed")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Webhook verification failed"
            )
            
    except Exception as e:
        logger.error(f"Error in Evolution API webhook verification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook verification error"
        )

@router.post("/whatsapp/webhook")
async def evolution_webhook_handler(request: Request):
    """
    Evolution API webhook message handler.
    
    This endpoint receives webhook events from Evolution API and processes
    incoming WhatsApp messages, sending AI responses back to users.
    
    Args:
        request (Request): The incoming webhook request from Evolution API
        
    Returns:
        dict: Success response
    """
    try:
        # Get the webhook payload
        payload = await request.json()
        logger.info(f"Received Evolution API webhook: {payload}")
        
        # Process the Evolution API message
        message_data = await process_whatsapp_message(payload)
        
        if message_data:
            # Process the incoming message and send AI response
            success = await process_incoming_message(message_data)
            
            if success:
                logger.info("Successfully processed incoming WhatsApp message")
            else:
                logger.warning("Failed to process incoming WhatsApp message")
        
        return {"status": "success", "message": "Webhook processed"}
        
    except Exception as e:
        logger.error(f"Error processing Evolution API webhook: {str(e)}")
        # Don't raise HTTP exception here - Evolution API expects 200 OK
        # Log the error but return success to avoid webhook retries
        return {"status": "error", "message": str(e)}

@router.post("/whatsapp/initialize")
async def initialize_whatsapp():
    """
    Initialize WhatsApp instance via Evolution API.
    
    This endpoint creates a new WhatsApp instance, sets up webhooks,
    and returns QR code for authentication if needed.
    
    Returns:
        dict: Initialization result with QR code if needed
    """
    try:
        logger.info("Initializing WhatsApp instance")
        result = await initialize_whatsapp_service()
        return result
        
    except Exception as e:
        logger.error(f"Error initializing WhatsApp instance: {str(e)}")
        raise HTTPException(
@router.get("/whatsapp/qr")
async def get_whatsapp_qr():
    """
    Get QR code for WhatsApp authentication.
    
    Returns:
        dict: QR code data for WhatsApp authentication
    """
    try:
        logger.info("Getting WhatsApp QR code")
        qr_data = await evolution_service.get_qr_code()
        return qr_data
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR code: {str(e)}"
        )
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
@router.get("/whatsapp/instance-status")
async def get_whatsapp_instance_status():
    """
    Get current WhatsApp instance connection status.
    
    Returns:
        dict: Instance connection status
    """
    try:
        logger.info("Getting WhatsApp instance status")
        status_data = await evolution_service.get_instance_status()
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp instance status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get instance status: {str(e)}"
        )
            detail=f"Failed to initialize WhatsApp instance: {str(e)}"
@router.post("/whatsapp/send-message")
async def send_message_endpoint(request: Request):
    """
    Send a WhatsApp message via Evolution API.
    
    Args:
        request (Request): Request with phone number and message
        
    Returns:
        dict: Message sending result
    """
    try:
        payload = await request.json()
        phone_number = payload.get("phone_number")
        message = payload.get("message")
        
        if not phone_number or not message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number and message are required"
            )
        
        logger.info(f"Sending WhatsApp message to {phone_number}")
        success = await send_whatsapp_message(phone_number, message)
        
        if success:
            return {"status": "success", "message": "Message sent successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in send message endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )
        )
@router.get("/whatsapp/status")
async def whatsapp_status():
    """
    Get the current status of the WhatsApp service via Evolution API.
    
    Returns:
        dict: Comprehensive WhatsApp service status
    """
    try:
        status_data = await get_whatsapp_service_status()
        
        # Add endpoint information
        status_data["endpoints"] = {
            "webhook_verification": "/api/v1/whatsapp/webhook (GET)",
            "webhook_handler": "/api/v1/whatsapp/webhook (POST)",
            "initialize": "/api/v1/whatsapp/initialize (POST)",
            "qr_code": "/api/v1/whatsapp/qr (GET)",
            "instance_status": "/api/v1/whatsapp/instance-status (GET)",
            "send_message": "/api/v1/whatsapp/send-message (POST)",
            "status": "/api/v1/whatsapp/status (GET)"
        }
        
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting WhatsApp status: {str(e)}")
        return {
            "service": "whatsapp",
            "status": "error",
            "error": str(e),
            "message": "Failed to get WhatsApp service status"
        }