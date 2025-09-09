"""
Firebase Service

This module handles Firebase Admin SDK integration for Firestore operations.
It provides secure initialization and helper functions for reading and writing
data to Firestore collections.

Configuration:
- Place your Firebase service account key in 'firebase-key.json' (gitignored)
- Or use environment variables for credentials
- Lawyers can update conversation flows directly in Firebase Console
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from fastapi import HTTPException, status

# Configure logging
logger = logging.getLogger(__name__)

# Global Firebase app instance
_firebase_app = None
_firestore_client = None

def initialize_firebase():
    """
    Initialize Firebase Admin SDK with credentials.
    
    This function initializes Firebase using either:
    1. Service account key file (firebase-key.json)
    2. Environment variables for credentials
    
    Only initializes once to avoid duplicate app errors.
    """
    global _firebase_app, _firestore_client
    
    if _firebase_app is not None:
        logger.info("Firebase already initialized")
        return
    
    try:
        # Method 1: Try to load from JSON file (recommended for development)
        key_file_path = "firebase-key.json"
        if os.path.exists(key_file_path):
            logger.info("Initializing Firebase with service account key file")
            cred = credentials.Certificate(key_file_path)
            _firebase_app = firebase_admin.initialize_app(cred)
        
        # Method 2: Try environment variables (recommended for production)
        elif all([
            os.getenv("FIREBASE_PROJECT_ID"),
            os.getenv("FIREBASE_CLIENT_EMAIL"),
            os.getenv("FIREBASE_PRIVATE_KEY")
        ]):
            logger.info("Initializing Firebase with environment variables")
            
            # Parse private key (handle escaped newlines)
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n')
            
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "private_key": private_key,
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID", ""),
                "client_id": os.getenv("FIREBASE_CLIENT_ID", ""),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
            }
            
            cred = credentials.Certificate(cred_dict)
            _firebase_app = firebase_admin.initialize_app(cred)
        
        else:
            raise ValueError("Firebase credentials not found. Please provide either firebase-key.json or environment variables.")
        
        # Initialize Firestore client
        _firestore_client = firestore.client()
        logger.info("Firebase initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase initialization failed: {str(e)}"
        )

def get_firestore_client():
    """
    Get the Firestore client instance.
    
    Returns:
        firestore.Client: The Firestore client
        
    Raises:
        HTTPException: If Firebase is not initialized
    """
    if _firestore_client is None:
        initialize_firebase()
    
    if _firestore_client is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Firestore client not available"
        )
    
    return _firestore_client

async def get_conversation_flow() -> Dict[str, Any]:
    """
    Retrieve the conversation flow configuration from Firestore.
    
    Lawyers can update this flow directly in Firebase Console without
    touching the code. The flow defines the guided pre-attendance questions.
    
    Returns:
        Dict[str, Any]: The conversation flow configuration
        
    Raises:
        HTTPException: If flow cannot be retrieved
    """
    try:
        db = get_firestore_client()
        
        # Get the conversation flow document
        flow_ref = db.collection('conversation_flows').document('law_firm_intake')
        flow_doc = flow_ref.get()
        
        if not flow_doc.exists:
            # Create default flow if it doesn't exist
            logger.info("Creating default conversation flow")
            default_flow = {
                "steps": [
                    {
                        "id": 1,
                        "question": "Hello! Welcome to our law firm. What is your full name?",
                        "field": "name",
                        "required": True
                    },
                    {
                        "id": 2,
                        "question": "Which area of law do you need help with?\n\n1. Penal Law\n2. Civil Law\n3. Labor Law\n4. Other\n\nPlease type the number or name:",
                        "field": "area_of_law",
                        "required": True
                    },
                    {
                        "id": 3,
                        "question": "Please describe your legal situation briefly. This will help us understand how we can assist you:",
                        "field": "situation",
                        "required": True
                    },
                    {
                        "id": 4,
                        "question": "Thank you for the information. Even if budget is a concern, we can work together to find a suitable payment plan. Would you like me to schedule a consultation with one of our lawyers?\n\nPlease answer: Yes or No",
                        "field": "wants_meeting",
                        "required": True
                    }
                ],
                "completion_message": "Thank you! Your information has been recorded and one of our lawyers will contact you soon. Do you have any other questions I can help you with?",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            flow_ref.set(default_flow)
            return default_flow
        
        flow_data = flow_doc.to_dict()
        logger.info("Retrieved conversation flow from Firestore")
        return flow_data
        
    except Exception as e:
        logger.error(f"Error retrieving conversation flow: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation flow"
        )

async def save_lead_data(lead_data: Dict[str, Any]) -> str:
    """
    Save lead information to Firestore.
    
    Args:
        lead_data (Dict[str, Any]): Lead information including name, area_of_law, etc.
        
    Returns:
        str: The document ID of the saved lead
        
    Raises:
        HTTPException: If lead cannot be saved
    """
    try:
        db = get_firestore_client()
        
        # Add timestamp and status
        lead_data.update({
            "timestamp": datetime.now(),
            "status": "new",
            "source": "chatbot_intake"
        })
        
        # Save to leads collection
        leads_ref = db.collection('leads')
        doc_ref = leads_ref.add(lead_data)
        
        doc_id = doc_ref[1].id
        logger.info(f"Saved lead data with ID: {doc_id}")
        return doc_id
        
    except Exception as e:
        logger.error(f"Error saving lead data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save lead information"
        )

async def get_user_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve user session data from Firestore.
    
    Args:
        session_id (str): The session identifier
        
    Returns:
        Optional[Dict[str, Any]]: Session data or None if not found
    """
    try:
        db = get_firestore_client()
        
        session_ref = db.collection('user_sessions').document(session_id)
        session_doc = session_ref.get()
        
        if session_doc.exists:
            return session_doc.to_dict()
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving session {session_id}: {str(e)}")
        return None

async def save_user_session(session_id: str, session_data: Dict[str, Any]) -> bool:
    """
    Save or update user session data in Firestore.
    
    Args:
        session_id (str): The session identifier
        session_data (Dict[str, Any]): Session data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        db = get_firestore_client()
        
        # Add/update timestamp
        session_data["last_updated"] = datetime.now()
        
        session_ref = db.collection('user_sessions').document(session_id)
        session_ref.set(session_data, merge=True)
        
        logger.info(f"Saved session data for: {session_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving session {session_id}: {str(e)}")
        return False

async def get_firebase_service_status() -> Dict[str, Any]:
    """
    Get the current status of the Firebase service.
    
    Returns:
        Dict[str, Any]: Status information about Firebase integration
    """
    try:
        # Test Firestore connection
        db = get_firestore_client()
        
        # Try to read a test document
        test_ref = db.collection('_health_check').document('test')
        test_ref.set({"timestamp": datetime.now(), "status": "healthy"})
        
        return {
            "service": "firebase_service",
            "status": "active",
            "firestore_connected": True,
            "collections": [
                "conversation_flows",
                "leads", 
                "user_sessions"
            ],
            "features": [
                "conversation_flow_management",
                "lead_data_storage",
                "session_management",
                "real_time_updates"
            ],
            "admin_access": "Firebase Console for flow updates"
        }
        
    except Exception as e:
        logger.error(f"Firebase service status check failed: {str(e)}")
        return {
            "service": "firebase_service",
            "status": "error",
            "firestore_connected": False,
            "error": str(e),
            "configuration_required": True
        }

# Initialize Firebase when module is imported
try:
    initialize_firebase()
except Exception as e:
    logger.warning(f"Firebase initialization deferred: {str(e)}")