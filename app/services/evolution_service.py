"""
Evolution API Service

This module provides integration with Evolution API for WhatsApp messaging.
It handles instance management, QR code generation, message sending, and webhook processing.
"""

import os
import httpx
import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

class EvolutionAPIService:
    """
    Service class for Evolution API integration.
    
    This class handles:
    - WhatsApp instance management
    - QR code generation and authentication
    - Message sending and receiving
    - Webhook processing
    - Connection status monitoring
    """
    
    def __init__(self):
        self.base_url = os.getenv("EVOLUTION_API_URL", "http://localhost:8080")
        self.api_key = os.getenv("EVOLUTION_API_KEY", "B6D711FCDE4D4FD5936544120E713976")
        self.instance_name = os.getenv("EVOLUTION_INSTANCE_NAME", "lawfirm_bot")
        self.webhook_url = os.getenv("EVOLUTION_WEBHOOK_URL", "http://host.docker.internal:8000/api/v1/whatsapp/webhook")
        self.test_number = os.getenv("WHATSAPP_TEST_NUMBER", "5511918368812")
        self.business_name = os.getenv("WHATSAPP_BUSINESS_NAME", "Law Firm Assistant")
        
        self.headers = {
            "Content-Type": "application/json",
            "apikey": self.api_key
        }
        
        self.timeout = httpx.Timeout(30.0)
    
    async def create_instance(self) -> Dict[str, Any]:
        """
        Create a new WhatsApp instance in Evolution API.
        
        Returns:
            Dict[str, Any]: Instance creation response
        """
        try:
            logger.info(f"Creating Evolution API instance: {self.instance_name}")
            
            payload = {
                "instanceName": self.instance_name,
                "token": self.api_key,
                "qrcode": True,
                "number": self.test_number,
                "webhook": self.webhook_url,
                "webhook_by_events": False,
                "webhook_base64": False,
                "events": [
                    "APPLICATION_STARTUP",
                    "QRCODE_UPDATED",
                    "CONNECTION_UPDATE",
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE",
                    "SEND_MESSAGE"
                ]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/instance/create",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Instance created successfully: {result}")
                    return result
                else:
                    error_text = response.text
                    logger.error(f"Failed to create instance: {response.status_code} - {error_text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to create Evolution API instance: {error_text}"
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Network error creating instance: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Network error connecting to Evolution API"
            )
        except Exception as e:
            logger.error(f"Unexpected error creating instance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create instance: {str(e)}"
            )
    
    async def get_instance_status(self) -> Dict[str, Any]:
        """
        Get the current status of the WhatsApp instance.
        
        Returns:
            Dict[str, Any]: Instance status information
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/instance/connectionState/{self.instance_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Instance status check failed: {response.status_code}")
                    return {"state": "close", "error": response.text}
                    
        except Exception as e:
            logger.error(f"Error getting instance status: {e}")
            return {"state": "error", "error": str(e)}
    
    async def get_qr_code(self) -> Dict[str, Any]:
        """
        Get the QR code for WhatsApp authentication.
        
        Returns:
            Dict[str, Any]: QR code data (base64 image and code)
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/instance/connect/{self.instance_name}",
                    headers=self.headers
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info("QR code retrieved successfully")
                    return result
                else:
                    error_text = response.text
                    logger.error(f"Failed to get QR code: {response.status_code} - {error_text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to get QR code: {error_text}"
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Network error getting QR code: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Network error connecting to Evolution API"
            )
        except Exception as e:
            logger.error(f"Unexpected error getting QR code: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get QR code: {str(e)}"
            )
    
    async def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """
        Send a WhatsApp message to a phone number.
        
        Args:
            phone_number (str): Target phone number (with country code)
            message (str): Message content
            
        Returns:
            Dict[str, Any]: Message sending response
        """
        try:
            # Format phone number (ensure it has country code)
            if not phone_number.startswith("55"):
                phone_number = f"55{phone_number}"
            
            # Remove any non-numeric characters except +
            phone_number = "".join(c for c in phone_number if c.isdigit())
            
            logger.info(f"Sending WhatsApp message to {phone_number}")
            
            payload = {
                "number": phone_number,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                },
                "textMessage": {
                    "text": message
                }
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/message/sendText/{self.instance_name}",
                    json=payload,
                    headers=self.headers
                )
                
                if response.status_code == 201:
                    result = response.json()
                    logger.info(f"Message sent successfully: {result}")
                    return result
                else:
                    error_text = response.text
                    logger.error(f"Failed to send message: {response.status_code} - {error_text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to send WhatsApp message: {error_text}"
                    )
                    
        except httpx.RequestError as e:
            logger.error(f"Network error sending message: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Network error connecting to Evolution API"
            )
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to send message: {str(e)}"
            )
    
    async def process_webhook_message(self, payload: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """
        Process incoming webhook message from Evolution API.
        
        Args:
            payload (Dict[str, Any]): Webhook payload
            
        Returns:
            Optional[Dict[str, str]]: Extracted message data
        """
        try:
            logger.info("Processing Evolution API webhook message")
            
            # Evolution API webhook structure
            if payload.get("event") == "messages.upsert":
                data = payload.get("data", {})
                
                if isinstance(data, dict):
                    # Single message
                    messages = [data]
                elif isinstance(data, list):
                    # Multiple messages
                    messages = data
                else:
                    return None
                
                for message in messages:
                    # Check if it's an incoming message (not from us)
                    if not message.get("key", {}).get("fromMe", True):
                        message_type = message.get("messageType", "")
                        
                        if message_type == "conversation":
                            return {
                                "message": message.get("message", {}).get("conversation", ""),
                                "from": message.get("key", {}).get("remoteJid", "").replace("@s.whatsapp.net", ""),
                                "id": message.get("key", {}).get("id", ""),
                                "timestamp": str(message.get("messageTimestamp", "")),
                                "instance": payload.get("instance", "")
                            }
                        elif message_type == "extendedTextMessage":
                            return {
                                "message": message.get("message", {}).get("extendedTextMessage", {}).get("text", ""),
                                "from": message.get("key", {}).get("remoteJid", "").replace("@s.whatsapp.net", ""),
                                "id": message.get("key", {}).get("id", ""),
                                "timestamp": str(message.get("messageTimestamp", "")),
                                "instance": payload.get("instance", "")
                            }
            
            return None
            
        except Exception as e:
            logger.error(f"Error processing webhook message: {e}")
            return None
    
    async def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive status of the Evolution API service.
        
        Returns:
            Dict[str, Any]: Service status information
        """
        try:
            # Test API connectivity
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/",
                    headers=self.headers
                )
                api_accessible = response.status_code == 200
            
            # Get instance status
            instance_status = await self.get_instance_status()
            
            return {
                "service": "evolution_api",
                "status": "active" if api_accessible else "error",
                "api_url": self.base_url,
                "api_accessible": api_accessible,
                "instance_name": self.instance_name,
                "instance_status": instance_status,
                "webhook_url": self.webhook_url,
                "test_number": self.test_number,
                "features": [
                    "whatsapp_messaging",
                    "qr_code_authentication",
                    "webhook_processing",
                    "message_sending",
                    "instance_management"
                ],
                "endpoints": {
                    "create_instance": f"{self.base_url}/instance/create",
                    "get_qr": f"{self.base_url}/instance/connect/{self.instance_name}",
                    "send_message": f"{self.base_url}/message/sendText/{self.instance_name}",
                    "instance_status": f"{self.base_url}/instance/connectionState/{self.instance_name}"
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting Evolution API service status: {e}")
            return {
                "service": "evolution_api",
                "status": "error",
                "error": str(e),
                "api_url": self.base_url
            }
    
    async def initialize_instance(self) -> Dict[str, Any]:
        """
        Initialize the WhatsApp instance (create if needed, get QR if not connected).
        
        Returns:
            Dict[str, Any]: Initialization result with QR code if needed
        """
        try:
            logger.info("Initializing Evolution API instance")
            
            # Check if instance exists and its status
            status = await self.get_instance_status()
            
            if status.get("state") == "close" or "error" in status:
                # Instance doesn't exist or is closed, create it
                logger.info("Creating new instance")
                create_result = await self.create_instance()
                
                # Wait a moment for instance to initialize
                await asyncio.sleep(2)
                
                # Get QR code for authentication
                qr_result = await self.get_qr_code()
                
                return {
                    "action": "created",
                    "instance": create_result,
                    "qr_code": qr_result,
                    "status": "needs_authentication",
                    "message": "Instance created. Please scan the QR code with WhatsApp."
                }
            
            elif status.get("state") == "connecting":
                # Instance is connecting, get QR code
                qr_result = await self.get_qr_code()
                
                return {
                    "action": "connecting",
                    "qr_code": qr_result,
                    "status": "needs_authentication",
                    "message": "Instance is connecting. Please scan the QR code with WhatsApp."
                }
            
            elif status.get("state") == "open":
                # Instance is already connected
                return {
                    "action": "already_connected",
                    "status": "connected",
                    "message": "WhatsApp instance is already connected and ready to use."
                }
            
            else:
                # Unknown state, try to get QR code
                try:
                    qr_result = await self.get_qr_code()
                    return {
                        "action": "reconnecting",
                        "qr_code": qr_result,
                        "status": "needs_authentication",
                        "message": "Reconnecting instance. Please scan the QR code with WhatsApp."
                    }
                except:
                    # If QR fails, create new instance
                    create_result = await self.create_instance()
                    await asyncio.sleep(2)
                    qr_result = await self.get_qr_code()
                    
                    return {
                        "action": "recreated",
                        "instance": create_result,
                        "qr_code": qr_result,
                        "status": "needs_authentication",
                        "message": "Instance recreated. Please scan the QR code with WhatsApp."
                    }
            
        except Exception as e:
            logger.error(f"Error initializing instance: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize WhatsApp instance: {str(e)}"
            )

# Global Evolution API service instance
evolution_service = EvolutionAPIService()