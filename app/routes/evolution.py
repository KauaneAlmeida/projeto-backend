"""
Evolution API Routes

Direct routes for Evolution API management and monitoring.
These endpoints provide direct access to Evolution API functionality
for administration and debugging purposes.
"""

from fastapi import APIRouter, HTTPException, status
from app.services.evolution_service import evolution_service
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.post("/evolution/initialize")
async def initialize_evolution_instance():
    """
    Initialize Evolution API WhatsApp instance.
    
    Creates a new instance, sets up webhooks, and returns QR code if needed.
    
    Returns:
        dict: Initialization result with QR code and status
    """
    try:
        logger.info("Initializing Evolution API instance")
        result = await evolution_service.initialize_instance()
        return result
        
    except Exception as e:
        logger.error(f"Error initializing Evolution API instance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Evolution API instance: {str(e)}"
        )

@router.get("/evolution/status")
async def get_evolution_status():
    """
    Get comprehensive Evolution API service status.
    
    Returns:
        dict: Service status including API connectivity and instance status
    """
    try:
        logger.info("Getting Evolution API service status")
        status_data = await evolution_service.get_service_status()
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting Evolution API status: {str(e)}")
        return {
            "service": "evolution_api",
            "status": "error",
            "error": str(e)
        }

@router.get("/evolution/qr")
async def get_evolution_qr():
    """
    Get QR code for WhatsApp authentication.
    
    Returns:
        dict: QR code data (base64 image and code)
    """
    try:
        logger.info("Getting Evolution API QR code")
        qr_data = await evolution_service.get_qr_code()
        return qr_data
        
    except Exception as e:
        logger.error(f"Error getting Evolution API QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR code: {str(e)}"
        )

@router.get("/evolution/instance-status")
async def get_evolution_instance_status():
    """
    Get current WhatsApp instance connection status.
    
    Returns:
        dict: Instance connection status and details
    """
    try:
        logger.info("Getting Evolution API instance status")
        status_data = await evolution_service.get_instance_status()
        return status_data
        
    except Exception as e:
        logger.error(f"Error getting Evolution API instance status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get instance status: {str(e)}"
        )

@router.post("/evolution/create-instance")
async def create_evolution_instance():
    """
    Create a new Evolution API WhatsApp instance.
    
    Returns:
        dict: Instance creation result
    """
    try:
        logger.info("Creating Evolution API instance")
        result = await evolution_service.create_instance()
        return result
        
    except Exception as e:
        logger.error(f"Error creating Evolution API instance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create instance: {str(e)}"
        )

@router.post("/evolution/send-test-message")
async def send_evolution_test_message():
    """
    Send a test message via Evolution API to the configured test number.
    
    Returns:
        dict: Message sending result
    """
    try:
        test_number = evolution_service.test_number
        test_message = "🤖 Test message from Law Firm AI Assistant via Evolution API! The integration is working correctly."
        
        logger.info(f"Sending test message to {test_number}")
        result = await evolution_service.send_message(test_number, test_message)
        
        return {
            "status": "success",
            "message": "Test message sent successfully",
            "target_number": test_number,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send test message: {str(e)}"
        )